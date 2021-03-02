'''
Unit tests for command line interface.

@author: Toni Magni
'''
import unittest
import logging
import os
import importlib.resources
import dicom4ortho.__main__
class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


    def tearDown(self):
        pass

    def testCli(self):
        resource_path = None
        with importlib.resources.path("test.resources","input_from.csv") as input_csv:
            testargs = ['',str(input_csv)]
            resource_path = os.path.dirname(input_csv)
        return_status = dicom4ortho.__main__.main(testargs)
        self.assertEqual(return_status, 0)
        assert os.path.exists(os.path.join(resource_path,'EV-01_EO.RP.LR.CO.dcm'))
        assert os.path.exists(os.path.join(resource_path,'EV-17_EO.FF.LC.CO.dcm'))
        assert os.path.exists(os.path.join(resource_path,'IV-25_IO.MX.MO.OV.WM.BC.dcm'))

    def testHelp(self):
        testargs = ['','-h']
        with self.assertRaises(SystemExit) as systemexit:
            dicom4ortho.__main__.main(testargs)
        self.assertEqual(systemexit.exception.code, 0)
