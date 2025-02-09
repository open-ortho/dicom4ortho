'''
Unittests for DICOM objects.

@author: Toni Magni
'''
import unittest
import logging
import importlib
from io import BytesIO
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dicom4ortho.controller import OrthodonticController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.config import StudyInstanceUID_ROOT, SeriesInstanceUID_ROOT
from dicom4ortho.utils import generate_dicom_uid, get_scheduled_protocol_code
from test.sample_data_generator import make_sample_MWL

from PIL import Image, ExifTags
from pydicom.dataset import Dataset

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


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
        input_image_filename=filename,
    )
    o.patient_firstname = "Michael"
    o.patient_lastname = "Jackson"
    o.patient_id = "X1"
    o.patient_birthdate = datetime(1958, 8, 29).date()
    o.patient_sex = "M"
    o.dental_provider_firstname = "Conrad"
    o.dental_provider_lastname = "Murray"
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

    def testEV01(self):
        """ Test that an image set as EV01 is tagged as expected.
        """
        o = photo_generator(
            image_type='EV-01', filename=Path('./test/resources/sample_NikonD90.JPG'))
        for tag in o._ds:
            print(f"{tag.tag} {tag.description()}: {tag.value}")

    def testDates(self):
        """ Test setting date and times with different formats and time zones.
        """
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

    def testExifTags(self):
        # Create an OrthodonticPhotograph using the sample MWL
        metadata = {
            'input_image_filename': self.resource_path / 'sample_NikonD90.JPG',
            'output_image_filename': 'output_image.dcm',
            'manufacturer': 'Test Manufacturer'
        }
        o = OrthodonticPhotograph(**metadata)
        o.prepare()

        # Assert that date/time tags were properly set from EXIF
        self.assertIsNotNone(o._ds.ContentDate, "ContentDate should be set from EXIF DateTime")
        self.assertIsNotNone(o._ds.ContentTime, "ContentTime should be set from EXIF DateTime")
        self.assertIsNotNone(o._ds.AcquisitionDateTime, "AcquisitionDateTime should be set from EXIF DateTime")
        
        # Check that the dates are in proper DICOM format
        self.assertTrue(len(o._ds.ContentDate) == 8, "ContentDate should be 8 characters YYYYMMDD")
        self.assertTrue(len(o._ds.ContentTime) == 13, "ContentTime should be 13 characters HHMMSS.FFFFFF")
        self.assertTrue(len(o._ds.AcquisitionDateTime) >= 19, "AcquisitionDateTime should be at least 19 characters YYYYMMDDHHMMSS.FFFFFF")

    def testProtocolCode(self):
        # Generate a sample MWL
        mwl = make_sample_MWL(modality='VL', startdate='20241209', starttime='090000')

        # Create an OrthodonticPhotograph using the sample MWL
        metadata = {
            'dicom_mwl': mwl,
            'input_image_filename': self.resource_path / 'sample_NikonD90.JPG',
            'output_image_filename': 'output_image.dcm',
            # 'image_type': 'EV20',
            # 'patient_firstname': 'John',
            # 'patient_lastname': 'Doe',
            # 'patient_id': '123456789',
            # 'patient_sex': 'M',
            # 'study_instance_uid': mwl.StudyInstanceUID,
            # 'series_instance_uid': mwl.ScheduledProcedureStepSequence[0].ScheduledProcedureStepID,
            # 'study_description': mwl.RequestedProcedureDescription,
            # 'series_description': mwl.ScheduledProcedureStepSequence[0].ScheduledProcedureStepDescription,
            'manufacturer': 'Test Manufacturer'
        }
        o = OrthodonticPhotograph(**metadata)
        o.copy_mwl_tags(dicom_mwl=mwl)
        # Set the instance number
        o.instance_number = '100'
        o.save()
        # Test the get_scheduled_protocol_code method
        scheduled_protocol_code = get_scheduled_protocol_code(o._ds)
        self.assertIsNotNone(scheduled_protocol_code, "Scheduled Protocol Code should not be None")
        self.assertEqual(scheduled_protocol_code.CodeValue, 'EV20', "Scheduled Protocol Code Value does not match")
        self.assertEqual(scheduled_protocol_code.CodingSchemeDesignator, '99OPOR', "Scheduled Protocol Coding Scheme Designator does not match")
        self.assertEqual(scheduled_protocol_code.CodeMeaning, 'Extraoral, Full Face, Full Smile, Centric Relation', "Scheduled Protocol Code Meaning does not match")



    @unittest.skip("I don't think NEF is read properly by Pillow")
    def testNEF(self):
        metadata = make_photo_metadata()
        metadata['input_image_filename'] = Path(
            ".") / "test" / "resources" / "DSC_0001.NEF"
        metadata['image_type'] = "IV05"
        c = OrthodonticController()
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
