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
from dicom4ortho.utils import jpeg2000_is_reversible

logger = logging.getLogger(__name__)

# Produced by topsOrtho, and lossy: the case that motivated preserving the
# codestream instead of re-encoding it.
TOPSORTHO_SAMPLE = Path('./test/resources/sample_topsOrtho.jp2')


def make_jpeg2000_bytes(lossless: bool) -> bytes:
    """A small JPEG 2000 image, compressed either reversibly or irreversibly."""
    image = Image.new('RGB', (64, 48), color=(120, 80, 40))
    buffer = io.BytesIO()
    if lossless:
        image.save(buffer, format='JPEG2000', quality_mode='lossless')
    else:
        image.save(buffer, format='JPEG2000', quality_mode='rates',
                   quality_layers=[20], irreversible=True)
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

    def test_raises_on_non_jpeg2000_input(self):
        """A caller passing the wrong format must be told, not given a guess."""
        with self.assertRaises(ValueError):
            jpeg2000_is_reversible(b'not a codestream')


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
