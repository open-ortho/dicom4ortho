"""Keep deprecation/resource cleanup behavior-preserving and warning-free."""

import gc
import io
import tempfile
import unittest
import warnings
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from dicom4ortho.model import PhotographBase
from test.test_e2e import compare_jpeg2dicom


class TestWarningCleanup(unittest.TestCase):
    """Removing deprecated image access must not alter encoded pixel bytes."""

    def test_raw_pixel_bytes_are_preserved_without_deprecation_warnings(self):
        grayscale = [0, 1, 127, 128, 254, 255]
        color = [(0, 1, 2), (3, 127, 255), (128, 64, 32),
                 (255, 0, 128), (12, 34, 56), (253, 254, 255)]
        cases = [
            ('1', (3, 3), [255, 0, 255, 0, 255, 0, 255, 0, 255], b'\xaa\x80'),
            ('L', (3, 2), grayscale, bytes(grayscale)),
            ('RGB', (3, 2), color, bytes(channel for pixel in color for channel in pixel)),
        ]
        for mode, size, pixels, expected in cases:
            with self.subTest(mode=mode):
                image = Image.new(mode, size)
                image.putdata(pixels)
                encoded = io.BytesIO()
                image.save(encoded, format='PNG')
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter('always', DeprecationWarning)
                    photograph = PhotographBase(input_image_bytes=encoded.getvalue())
                dataset = photograph.to_dataset()
                self.assertEqual(dataset.PixelData, expected)
                self.assertEqual((dataset.Columns, dataset.Rows), size)
                self.assertEqual([str(item.message) for item in captured], [])

    def test_jpeg_comparison_does_not_emit_deprecation_or_resource_warnings(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = directory / 'first.jpg'
            second = directory / 'second.jpg'
            Image.new('RGB', (8, 8), (120, 80, 40)).save(first, format='JPEG')
            Image.new('RGB', (8, 8), (40, 120, 80)).save(second, format='JPEG')
            for source, expected in ((first, True), (second, False)):
                with self.subTest(matches=expected):
                    dicom = directory / 'image.dcm'
                    PhotographBase(
                        input_image_filename=source, output_image_filename=dicom).save()
                    with warnings.catch_warnings(record=True) as captured:
                        warnings.simplefilter('always', DeprecationWarning)
                        warnings.simplefilter('always', ResourceWarning)
                        if expected:
                            self.assertTrue(compare_jpeg2dicom(first, dicom))
                        else:
                            with self.assertLogs('dicom4ortho', level='ERROR'):
                                self.assertFalse(compare_jpeg2dicom(first, dicom))
                        gc.collect()
                    self.assertEqual([str(item.message) for item in captured], [])

    def test_pixel_comparison_supports_older_pillow(self):
        from test.test_e2e import _pixel_values

        old_image = SimpleNamespace(getdata=lambda: [(1, 2, 3)])
        self.assertEqual(_pixel_values(old_image), [(1, 2, 3)])
