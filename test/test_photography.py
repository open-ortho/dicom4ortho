'''
Unittests for DICOM objects.

@author: Toni Magni
'''
import unittest
import logging
import importlib
from io import BytesIO
import dicom4ortho.m_orthodontic_photograph
from dicom4ortho.controller import SimpleController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.defaults import generate_dicom_uid
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ExifTags
from pydicom.dataset import Dataset

def make_photo_metadata():
    metadata = {
        "patient_firstname": "Michael",
        "patient_lastname": "Jackson",
        "patient_id": "X1",
        "patient_sex": "M",
        "patient_birthdate": "1958-08-29",
        "dental_provider_firstname": "Conrad",
        "dental_provider_lastname": "Murray",
        "study_instance_uid": generate_dicom_uid(),
        "series_instance_uid": generate_dicom_uid(),
        "series_description": "UnitTest make_photo_metadata",
        "days_after_event": 212,
        "treatment_event_type": "OrthodonticTreatment"
    }
    return metadata


def photo_generator(image_type: str, filename: Path) -> OrthodonticPhotograph:
    o = OrthodonticPhotograph(
        image_type=image_type,
    )
    o.patient_firstname = "Michael"
    o.patient_lastname = "Jackson"
    o.patient_id = "X1"
    o.patient_birthdate = datetime(1958, 8, 29).date()
    o.patient_sex = "M"
    o.dental_provider_firstname = "Conrad"
    o.dental_provider_lastname = "Murray"
    o.input_image_filename = filename
    o.output_image_filename = o.input_image_filename.with_suffix(".dcm")
    return o

def compare_images(jpeg_image_file_path, dicom_image_file_path):
    def are_linearly_related(tuple1, tuple2, tolerance=0.01):
        """
        Checks if the components of two pixel tuples are linearly related within a tolerance.

        Args:
        tuple1 (tuple): The first RGB pixel tuple.
        tuple2 (tuple): The second RGB pixel tuple.
        tolerance (float): The allowable difference in ratios to still be considered linear.

        Returns:
        bool: True if linearly related within tolerance, False otherwise.
        """
        # Prevent division by zero and handle zero case comparisons
        if any(x == 0 for x in tuple1) or any(y == 0 for y in tuple2):
            return False

        # Compute ratios
        ratios = []
        for a, b in zip(tuple1, tuple2):
            if b == 0:  # Prevent division by zero
                return (False, None)
            ratios.append(a / b)

        # Check if ratios are approximately the same
        first_ratio = ratios[0]
        for ratio in ratios[1:]:
            if not (first_ratio - tolerance <= ratio <= first_ratio + tolerance):
                return (False,ratios)

        return (True,ratios)

        # Example usage:
        # tuple1 = (100, 200, 150)
        # tuple2 = (10, 20, 15)
        # print(are_linearly_related(tuple1, tuple2))  # Output should be True if they are linearly related

    # This function should implement the pixel by pixel comparison.
    # Example placeholder logic:
    from PIL import Image
    import pydicom

    # Load JPEG image
    jpeg_img = Image.open(jpeg_image_file_path).convert('RGB')
    jpeg_pixels = jpeg_img.getdata()

    # Load DICOM image
    dicom_img = pydicom.dcmread(dicom_image_file_path)
    try:
        dicom_array = dicom_img.pixel_array
    except Exception as e:
        print("Error processing DICOM pixel data:", e)
        print("DICOM Tags:", dicom_img.dir())  # This will print available DICOM tags
        raise

    if 'PhotometricInterpretation' in dicom_img and dicom_img.PhotometricInterpretation == 'YBR_FULL':
        import cv2
        dicom_array = cv2.cvtColor(dicom_array, cv2.COLOR_YCrCb2RGB)

    # Convert DICOM pixel array to Image for comparison
    dicom_image = Image.fromarray(dicom_array)
    dicom_pixels = dicom_image.getdata()

    # Compare each pixel
    if len(jpeg_pixels) != len(dicom_pixels):
        print(f"\nFAIL: JPEG size [{len(jpeg_pixels)}] != DICOM size [{len(dicom_pixels)}]")
        return False
    print(f"\nPASS size test: both JPEG and DICOM have same size of [{len(dicom_pixels)}].")

    pixel_index = 0
    differences = 0
    for jp, dp in zip(jpeg_pixels, dicom_pixels):
        if jp != dp:
            related, ratios = are_linearly_related(jp,dp)
            if not related:
                print(f"FAIL: at [{pixel_index}] JPEG pixel is [{jp}], DICOM pixel is [{dp}], ratios: [{ratios}]")
                differences += 1
        else:
            print(f"PASS: at [{pixel_index}] JPEG pixel is [{jp}], DICOM pixel is [{dp}]")
        pixel_index += 1

    if differences == 0:
        return True
    else:
        print(f"FAIL: with [{differences}] different pixels.")
        return False


class PhotoTests(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                            level=logging.INFO)
        self.resource_path = None
        with importlib.resources.path("test.resources","input_from.csv") as input_csv:
            self.resource_path = Path(input_csv).parent.absolute()

    def tearDown(self):
        pass

    def testDates(self):
        o = OrthodonticPhotograph()
        o.study_datetime = datetime(1592, 2, 3, 12, 14, 11)
        self.assertEqual(o._ds.StudyDate, "15920203")
        self.assertEqual(o._ds.StudyTime, "121411.000000")
        self.assertEqual(o.study_datetime, datetime(1592, 2, 3, 12, 14, 11))

        o.series_datetime = datetime(1492, 2, 3, 13, 14)
        self.assertEqual(o._ds.SeriesDate, "14920203")
        self.assertEqual(o._ds.SeriesTime, "131400.000000")
        self.assertEqual(o.series_datetime, datetime(1492, 2, 3, 13, 14))

        o.timezone = timezone(timedelta(hours=+1))
        o.acquisition_datetime = datetime(1992, 2, 3, 12, 14, 11)
        self.assertEqual(o._ds.AcquisitionDateTime,
                         "19920203121411.000000+0100")
        self.assertEqual(o._ds.AcquisitionDate, "19920203")
        self.assertEqual(o._ds.AcquisitionTime, "121411.000000")

        o.timezone = timezone(timedelta(hours=-9))
        self.assertEqual(o._ds.TimezoneOffsetFromUTC, "-0900")
        self.assertEqual(o.timezone, timezone(timedelta(hours=-9)))

        o.set_time_captured(datetime(1993, 10, 12, 22, 32, 43))
        self.assertEqual(o._ds.AcquisitionDateTime,
                         "19931012223243.000000-0900")
        self.assertEqual(o._ds.AcquisitionDate, "19931012")
        self.assertEqual(o._ds.AcquisitionTime, "223243.000000")
        self.assertEqual(o._ds.ContentDate, "19931012")
        self.assertEqual(o._ds.ContentTime, "223243.000000")

    def testProgress(self):
        md = make_photo_metadata()
        md["days_after_event"] = 212
        md["treatment_event_type"] = "OrthodonticTreatment"
        md["image_type"] = "EV08"
        o = OrthodonticPhotograph(**md)
        o._set_dicom_attributes()

        self.assertEqual(o._ds.AcquisitionContextSequence[3].NumericValue,212)


    def testNames(self):
        o = OrthodonticPhotograph()
        o.dental_provider_firstname = "Toni"
        self.assertEqual(o._ds.ReferringPhysicianName, "^Toni")

        o = OrthodonticPhotograph()
        o.dental_provider_lastname = "Magni"
        self.assertEqual(o._ds.ReferringPhysicianName, "Magni^")

        o = OrthodonticPhotograph()
        o.dental_provider_firstname = "Toni"
        o.dental_provider_lastname = "Magni"
        self.assertEqual(o._ds.ReferringPhysicianName, "Magni^Toni")
        self.assertEqual(o.dental_provider_firstname, "Toni")
        self.assertEqual(o.dental_provider_lastname, "Magni")
        myio = BytesIO()
        o.save_implicit_little_endian(myio)

        o = OrthodonticPhotograph()
        o.patient_firstname = "Toni"
        self.assertEqual(o._ds.PatientName, "^Toni")

        o = OrthodonticPhotograph()
        o.patient_lastname = "Magni"
        self.assertEqual(o._ds.PatientName, "Magni^")

        o = OrthodonticPhotograph()
        o.patient_firstname = "Toni"
        o.patient_lastname = "Magni"
        self.assertEqual(o._ds.PatientName, "Magni^Toni")
        self.assertEqual(o.patient_firstname, "Toni")
        self.assertEqual(o.patient_lastname, "Magni")

        o = OrthodonticPhotograph()
        o.operator_firstname = "Toni"
        self.assertEqual(o._ds.OperatorsName, "^Toni")

        o = OrthodonticPhotograph()
        o.operator_lastname = "Magni"
        self.assertEqual(o._ds.OperatorsName, "Magni^")

        o = OrthodonticPhotograph()
        o.operator_firstname = "Toni"
        o.operator_lastname = "Magni"
        self.assertEqual(o._ds.OperatorsName, "Magni^Toni")
        self.assertEqual(o.operator_firstname, "Toni")
        self.assertEqual(o.operator_lastname, "Magni")

    @unittest.skip("I don't think NEF is read properly by Pillow")
    def testNEF(self):
        metadata = make_photo_metadata()
        metadata['input_image_filename'] = Path(
            ".") / "test" / "resources" / "DSC_0001.NEF"
        metadata['image_type'] = "IV05"
        c = SimpleController()
        c.convert_image_to_dicom4orthograph(metadata=metadata)

    def test_NikonD90(self):
        """ Test the various images produced by the Nikon D90 Camera.
        """

        metadata = make_photo_metadata()
        metadata['input_image_filename'] = self.resource_path / "sample_NikonD90.JPG"
        metadata['image_type'] = "IV06"
        c = SimpleController()
        c.convert_image_to_dicom4orthograph_and_save(metadata=metadata)
        output_file = (self.resource_path / "sample_NikonD90.dcm")
        self.assertTrue(output_file.exists())
        self.assertTrue(compare_images(
            jpeg_image_file_path=metadata["input_image_filename"],
            # dicom_image_file_path=(self.resource_path / "d90.dcm")))
            dicom_image_file_path=output_file))
        output_file.unlink()


    def test_JPG(self):
        metadata = make_photo_metadata()
        metadata['input_image_filename'] = self.resource_path / "sample_NikonD5600.JPG"
        metadata['image_type'] = "IV06"
        c = SimpleController()
        c.convert_image_to_dicom4orthograph_and_save(metadata=metadata)
        output_file = self.resource_path / "sample_NikonD5600.dcm"
        self.assertTrue(output_file.exists())
        output_file.unlink()

        metadata = make_photo_metadata()
        metadata['input_image_filename'] = self.resource_path / "sample_topsOrtho.jp2"
        metadata['image_type'] = "IV06"
        c = SimpleController()
        c.convert_image_to_dicom4orthograph_and_save(metadata=metadata)
        output_file = (self.resource_path / "sample_topsOrtho.dcm")
        self.assertTrue(output_file.exists())
        c.validate_dicom_file()
        output_file.unlink()

    @unittest.skip("Just a tool, not a test")
    def testEXIF(self):
        filename = Path(
            # ".") / "test" / "resources" / "sample_topsOrtho.jp2"
            ".") / "test" / "resources" / "sample_NikonD90.JPG"
        with Image.open(filename) as img:
            exif_ifd = img.getexif().getifd
            exif_raw = img.getexif().items()
            for tag in exif_raw:
                print(f"{tag}")
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in exif_raw
                if k in ExifTags.TAGS
            }
        for tag in exif.items():
            print(f"{tag}")


@unittest.skip("Just a tool, not a test")
class MPO(unittest.TestCase):
    def testsplitMPO(self):
        filename = Path(
            ".") / "test" / "resources" / "DSC_0001.JPG"
        with Image.open(filename) as img:
            num_frames = getattr(img, "n_frames", 1)
            logging.info(f"Found {num_frames} frames in {img.format} image")
            for i in range(num_frames):
                outputfilename = Path(f"{filename.stem}_{i}{filename.suffix}")
                img.seek(i)
                img.save(outputfilename, format='jpeg')

        self.assertTrue(outputfilename.exists())
