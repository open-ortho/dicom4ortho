'''
Unit tests for model classes.

@author: Toni Magni
'''
from unittest import TestCase
import logging
from dicom4ortho.m_ada1107 import ADA1107
from dicom4ortho.model import DicomBase

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s', level=logging.INFO)


class Test(TestCase):

    def test_load_views(self):
        v = ADA1107()
        self.assertEquals(len(v.VIEWS), 74)
        self.assertGreater(len(v.VIEWS["VERSION"]), 0)
        self.assertGreater(len(v.CODES["VERSION"]), 0)
        logging.info(
            f'Views ver: [{v.VIEWS["VERSION"]}] Codes ver: [{v.CODES["VERSION"]}]')


class DicomBaseTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_acquisition_datetime(self):
        db = DicomBase()

