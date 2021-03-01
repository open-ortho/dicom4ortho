'''
Created on Jul 3, 2018

@author: afm
'''
import unittest
import logging
import dicom4ortho.m_orthodontic_photograph

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

    # def test_newfile(self):
    #     photograph

#     def timezone_offset_seconds(self,server_info):
#         '''
#         This is a copy from topsServe_rollmonitor, because i want to make sure
#         if that one gets modified and breaks, this ones doesn't.
#
#         Convert the timezone string in server_info into a signed integer of seconds.
