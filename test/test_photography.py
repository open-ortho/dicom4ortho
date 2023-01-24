'''
Unittests for DICOM objects.

@author: Toni Magni
'''
import unittest
import logging
import dicom4ortho.m_orthodontic_photograph
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from datetime import datetime, timezone, timedelta
from pathlib import Path

from pydicom.dataset import Dataset
# Just importing will do to execute the code in the module. Pylint will
# complain though.
# pylint: disable=unused-import
import dicom4ortho.m_dental_acquisition_context_module
class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


    def tearDown(self):
        pass

    def testOne(self):
        ds = Dataset()
        for f in dicom4ortho.m_orthodontic_photograph.IMAGE_TYPES['EV01']:
            f(ds)
        logging.debug("{}".format(ds))

        self.assertEqual(ds.ImageLaterality,'U')

    def testDates(self):
        o = OrthodonticPhotograph()
        o.study_datetime = datetime(1592,2,3,12,14,11)
        self.assertEqual(o._ds.StudyDate, "15920203")
        self.assertEqual(o._ds.StudyTime, "121411.000000")
        self.assertEqual(o.study_datetime, datetime(1592,2,3,12,14,11))

        o.series_datetime = datetime(1492,2,3,13,14)
        self.assertEqual(o._ds.SeriesDate, "14920203")
        self.assertEqual(o._ds.SeriesTime, "131400.000000")
        self.assertEqual(o.series_datetime, datetime(1492,2,3,13,14))
    
        o.acquisition_datetime = datetime(1992,2,3,12,14,11)
        self.assertEqual(o._ds.AcquisitionDateTime, "19920203121411.000000+0100")
        self.assertEqual(o._ds.AcquisitionDate, "19920203")
        self.assertEqual(o._ds.AcquisitionTime, "121411.000000")

        o.timezone = timezone(timedelta(hours=-9))
        self.assertEqual(o._ds.TimezoneOffsetFromUTC, "-0900")
        self.assertEqual(o.timezone, timezone(timedelta(hours=-9)))

        o.set_time_captured(datetime(1993,10,12,22,32,43))
        self.assertEqual(o._ds.AcquisitionDateTime, "19931012223243.000000+0200")
        self.assertEqual(o._ds.AcquisitionDate, "19931012")
        self.assertEqual(o._ds.AcquisitionTime, "223243.000000")
        self.assertEqual(o._ds.ContentDate, "19931012")
        self.assertEqual(o._ds.ContentTime, "223243.000000")

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

    @unittest.skip("No NEF file uploaded to repository")
    def testNEF(self):
        o = OrthodonticPhotograph()
        o.input_image_filename = (Path(".") / "test" / "DSC_0001.NEF")
        o.output_image_filename = o.input_image_filename.with_suffix(".dcm")
        o.set_image()
        o.save_implicit_little_endian()