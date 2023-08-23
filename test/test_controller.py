'''
Unit tests for controller.

@author: Toni Magni
'''
import unittest
import logging
import logging
import dicom4ortho.defaults as defaults
import dicom4ortho.controller as controller

class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


    def tearDown(self):
        pass
