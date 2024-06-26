'''
Unittests for DICOM objects.

@author: Toni Magni
'''
import io
import unittest
import logging
import importlib
from io import BytesIO
import dicom4ortho.m_orthodontic_photograph
from dicom4ortho.controller import SimpleController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.defaults import generate_dicom_uid, StudyInstanceUID_ROOT, SeriesInstanceUID_ROOT
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ExifTags
from pydicom.dataset import Dataset

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO)


def make_photo_metadata():
    metadata = {
        "patient_firstname": "Michael",
        "patient_lastname": "Jackson",
        "patient_id": "X1",
        "patient_sex": "M",
        "patient_birthdate": "1958-08-29",
        "dental_provider_firstname": "Conrad",
        "dental_provider_lastname": "Murray",
        "study_instance_uid": generate_dicom_uid(root=StudyInstanceUID_ROOT),
        "series_instance_uid": generate_dicom_uid(root=SeriesInstanceUID_ROOT),
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



class PhotoTests(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                            level=logging.INFO)
        self.resource_path = None
        with importlib.resources.path("test.resources", "input_from.csv") as input_csv:
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

        self.assertEqual(o._ds.AcquisitionContextSequence[3].NumericValue, 212)

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

    
    @unittest.skip("Just a tool, not a test")
    def testEXIF(self):
        filename = Path(
            # ".") / "test" / "resources" / "sample_topsOrtho.jp2"
            self.resource_path / "sample_NikonD90.JPG")
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
    def testsplitMPO(self):
        filename = Path(
            self.resource_path / "DSC_0001.JPG")
        with Image.open(filename) as img:
            num_frames = getattr(img, "n_frames", 1)
            logging.info(f"Found {num_frames} frames in {img.format} image")
            for i in range(num_frames):
                outputfilename = Path(f"{filename.stem}_{i}{filename.suffix}")
                img.seek(i)
                img.save(outputfilename, format='jpeg')

        self.assertTrue(outputfilename.exists())
