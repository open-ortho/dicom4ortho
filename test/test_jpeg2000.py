'''
Unittests for JPEG 2000 encapsulation.

Covers that a JPEG 2000 source is stored verbatim under a Transfer Syntax that
matches how it was actually compressed, rather than being decoded and re-encoded.
'''
import io
import logging
import unittest
from pathlib import Path

from PIL import Image
from pydicom.encaps import generate_pixel_data_frame
from pydicom.uid import JPEG2000, JPEG2000Lossless

from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.utils import jpeg2000_codestream, jpeg2000_is_reversible

logger = logging.getLogger(__name__)

# Exported by TOPS, and lossy: the case that motivated preserving the codestream
# instead of re-encoding it. TOPS names these files ".jp2" even though their
# contents are a bare codestream, so the fixture is stored under the extension
# that matches its bytes. test_topsortho_sample_is_a_codestream_not_a_container
# pins that.
TOPSORTHO_SAMPLE = Path('./test/resources/sample_topsOrtho.j2k')

# The 12-byte JP2 signature box, ISO/IEC 15444-1 Annex I.5.1.
JP2_SIGNATURE = b'\x00\x00\x00\x0c\x6a\x50\x20\x20\x0d\x0a\x87\x0a'
SOC_MARKER = b'\xff\x4f'


def make_jpeg2000_bytes(lossless: bool, container: bool = False) -> bytes:
    """A small JPEG 2000 image, compressed either reversibly or irreversibly.

    Returns a bare codestream by default. With container=True it returns a
    genuine JP2 file: signature box, ftyp, jp2h and the codestream inside jp2c.
    """
    image = Image.new('RGB', (64, 48), color=(120, 80, 40))
    buffer = io.BytesIO()
    options = {'no_jp2': not container}
    if lossless:
        image.save(buffer, format='JPEG2000', quality_mode='lossless', **options)
    else:
        image.save(buffer, format='JPEG2000', quality_mode='rates',
                   quality_layers=[20], irreversible=True, **options)
    return buffer.getvalue()


def photograph_from_bytes(image_bytes: bytes) -> OrthodonticPhotograph:
    photo = OrthodonticPhotograph(
        image_type='EV-01',
        input_image_bytes=image_bytes,
        patient_firstname='Michael',
        patient_lastname='Jackson',
        patient_id='X1',
    )
    photo.prepare()
    return photo


class JPEG2000ReversibilityTests(unittest.TestCase):
    """jpeg2000_is_reversible() reads compression from the codestream header."""

    def test_detects_lossless_codestream(self):
        self.assertTrue(jpeg2000_is_reversible(make_jpeg2000_bytes(lossless=True)))

    def test_detects_lossy_codestream(self):
        self.assertFalse(jpeg2000_is_reversible(make_jpeg2000_bytes(lossless=False)))

    def test_detects_lossy_topsortho_sample(self):
        """The real-world sample this change was written for is lossy."""
        self.assertFalse(jpeg2000_is_reversible(TOPSORTHO_SAMPLE.read_bytes()))

    def test_reads_compression_through_a_jp2_container(self):
        """The wavelet is a property of the codestream, wrapped or not."""
        self.assertTrue(jpeg2000_is_reversible(
            make_jpeg2000_bytes(lossless=True, container=True)))
        self.assertFalse(jpeg2000_is_reversible(
            make_jpeg2000_bytes(lossless=False, container=True)))

    def test_raises_on_non_jpeg2000_input(self):
        """A caller passing the wrong format must be told, not given a guess."""
        with self.assertRaises(ValueError):
            jpeg2000_is_reversible(b'not a codestream')


class JPEG2000CodestreamTests(unittest.TestCase):
    """jpeg2000_codestream() unwraps a JP2 container and passes through a codestream."""

    def test_a_codestream_is_returned_unchanged(self):
        image_bytes = make_jpeg2000_bytes(lossless=False)
        self.assertEqual(jpeg2000_codestream(image_bytes), image_bytes)

    def test_a_container_yields_the_codestream_inside_it(self):
        container = make_jpeg2000_bytes(lossless=True, container=True)
        self.assertTrue(container.startswith(JP2_SIGNATURE),
                        "fixture is not a JP2 container, so this proves nothing")

        codestream = jpeg2000_codestream(container)

        self.assertTrue(codestream.startswith(SOC_MARKER))
        self.assertLess(len(codestream), len(container),
                        "the container's boxes should have been dropped")
        self.assertIn(codestream, container)

    def test_topsortho_sample_is_a_codestream_not_a_container(self):
        """The fixture does not exercise container handling, and must not appear to.

        TOPS exports these under a .jp2 name even though they hold no boxes, which
        is why format has to be read from the bytes and not from the extension.
        """
        image_bytes = TOPSORTHO_SAMPLE.read_bytes()

        self.assertTrue(image_bytes.startswith(SOC_MARKER))
        self.assertFalse(image_bytes.startswith(JP2_SIGNATURE))
        self.assertEqual(jpeg2000_codestream(image_bytes), image_bytes)

    def test_rejects_input_that_is_neither(self):
        with self.assertRaises(ValueError):
            jpeg2000_codestream(b'not a codestream')

    def test_rejects_a_container_without_a_codestream_box(self):
        """A truncated container must fail, not encapsulate its boxes."""
        container = make_jpeg2000_bytes(lossless=True, container=True)
        without_codestream = container[:container.index(b'jp2c') - 4]

        with self.assertRaises(ValueError):
            jpeg2000_codestream(without_codestream)


class JPEG2000EncapsulationTests(unittest.TestCase):
    """_set_image_jpeg2000_data() stores the source codestream unchanged."""

    def assertEncapsulates(self, photo: OrthodonticPhotograph, image_bytes: bytes):
        """Assert PixelData holds exactly this codestream.

        Encapsulated fragments must have an even length (PS3.5 A.4), so an
        odd-length codestream is legitimately stored with one trailing pad byte.
        Anything beyond that means the codestream was altered.
        """
        # pylint: disable=protected-access
        frame = next(generate_pixel_data_frame(photo._ds.PixelData))
        self.assertEqual(frame[:len(image_bytes)], image_bytes)
        self.assertLessEqual(len(frame) - len(image_bytes), 1,
                             "codestream was re-encoded, not stored verbatim")

    def test_lossless_source_is_tagged_lossless_only(self):
        image_bytes = make_jpeg2000_bytes(lossless=True)
        photo = photograph_from_bytes(image_bytes)

        # pylint: disable=protected-access
        self.assertEqual(photo._ds.file_meta.TransferSyntaxUID, JPEG2000Lossless)
        self.assertEqual(photo._ds.LossyImageCompression, '00')
        self.assertNotIn('LossyImageCompressionMethod', photo._ds)

    def test_lossy_source_is_tagged_lossy(self):
        image_bytes = make_jpeg2000_bytes(lossless=False)
        photo = photograph_from_bytes(image_bytes)

        # pylint: disable=protected-access
        self.assertEqual(photo._ds.file_meta.TransferSyntaxUID, JPEG2000)
        self.assertEqual(photo._ds.LossyImageCompression, '01')
        self.assertEqual(photo._ds.LossyImageCompressionMethod, 'ISO_15444_1')

    def test_source_codestream_is_encapsulated_unchanged(self):
        """Re-encoding would alter the bytes and inflate an already lossy image."""
        image_bytes = make_jpeg2000_bytes(lossless=False)
        photo = photograph_from_bytes(image_bytes)

        self.assertEncapsulates(photo, image_bytes)

    def test_a_jp2_container_is_unwrapped_before_encapsulation(self):
        """Pixel Data holds the codestream, never the boxes around it.

        A JPEG 2000 Transfer Syntax describes a codestream, so storing a whole
        container would leave the dataset advertising something its own Pixel Data
        is not, and conformant decoders may refuse it.
        """
        container = make_jpeg2000_bytes(lossless=True, container=True)
        self.assertTrue(container.startswith(JP2_SIGNATURE),
                        "fixture is not a JP2 container, so this proves nothing")
        photo = photograph_from_bytes(container)

        self.assertEncapsulates(photo, jpeg2000_codestream(container))
        # pylint: disable=protected-access
        frame = next(generate_pixel_data_frame(photo._ds.PixelData))
        self.assertFalse(frame.startswith(JP2_SIGNATURE))
        self.assertEqual(photo._ds.file_meta.TransferSyntaxUID, JPEG2000Lossless)

    def test_topsortho_sample_is_not_inflated(self):
        """A lossy source used to grow several-fold by being re-encoded losslessly."""
        image_bytes = TOPSORTHO_SAMPLE.read_bytes()
        photo = photograph_from_bytes(image_bytes)

        self.assertEncapsulates(photo, image_bytes)
        # pylint: disable=protected-access
        self.assertEqual(photo._ds.file_meta.TransferSyntaxUID, JPEG2000)
        self.assertEqual(photo._ds.Columns, 2048)
        self.assertEqual(photo._ds.Rows, 1411)


if __name__ == '__main__':
    unittest.main()
