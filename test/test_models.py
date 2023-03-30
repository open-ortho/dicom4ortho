'''
Unit tests for model classes.

@author: Toni Magni
'''
import unittest
import logging
from dicom4ortho.m_ada1107 import ADA1107

class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)

    def test_load_views(self):
        v = ADA1107()
        self.assertEquals(len(v.VIEWS), 74)
        self.assertGreater(len(v.VIEWS["VERSION"]),0)
        self.assertGreater(len(v.CODES["VERSION"]),0)
        logging.info(f'Views ver: [{v.VIEWS["VERSION"]}] Codes ver: [{v.CODES["VERSION"]}]')