'''
Unittests for DICOM objects.

@author: Toni Magni
'''
import unittest
import logging
import dicom4ortho.m_orthodontic_photograph
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from datetime import datetime, timezone, timedelta

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
