'''
Unit tests for command line interface.

@author: Toni Magni
'''
import io
import unittest
import logging
from pathlib import Path
from unittest.mock import patch

import dicom4ortho.__main__
from pydicom import dcmread


class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


    def tearDown(self):
        pass

    def testCli(self):
        examples_path = Path(__file__).resolve().parent.parent / 'examples'
        input_csv = examples_path / 'input_from.csv'
        testargs = ['', str(input_csv)]
        return_status = dicom4ortho.__main__.main(testargs)
        self.assertEqual(return_status, 0)

        output_files = [
            examples_path / 'EV-01_EO.RP.LR.CO.dcm',
            examples_path / 'EV-17_EO.FF.LC.CO.dcm',
            examples_path / 'IV-25_IO.MX.MO.OV.WM.BC.dcm',
        ]
        for output_file in output_files:
            self.addCleanup(output_file.unlink, missing_ok=True)
            self.assertTrue(output_file.exists())

        ds = dcmread(output_files[0])
        self.assertEqual(ds.PhysiciansOfRecord, 'Angle^Edward')
        self.assertEqual(ds.OperatorsName, 'Jordan^Alex')
        self.assertEqual(ds.ReferringPhysicianName, '')

    def testHelp(self):
        testargs = ['','-h']
        with self.assertRaises(SystemExit) as systemexit:
            dicom4ortho.__main__.main(testargs)
        self.assertEqual(systemexit.exception.code, 0)

    def testListImageTypes(self):
        testargs = ['', 'list-image-types']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            return_status = dicom4ortho.__main__.main(testargs)
        self.assertEqual(return_status, 0)
        output = mock_stdout.getvalue()
        self.assertIn('Type', output)
        self.assertIn('Abbreviated', output)
        self.assertIn('Full Meaning', output)
        # Spot-check a known image type from the generated ADA FHIR terminology.
        self.assertIn('EV01', output)
        self.assertIn('EO.RP.LR.CO', output)
