'''
Unit tests for controller.

@author: Toni Magni
'''
import unittest
import logging
import os
import logging
import importlib.resources
import dicom4ortho.__main__
import dicom4ortho.defaults as defaults
import dicom4ortho.controller as controller

class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=logging.INFO)


    def tearDown(self):
        pass

    def test_load_image_types(self):
        c = controller.SimpleController(None)
        self.assertEqual(defaults.image_types['EV01'][0], "EO.RP.LR.CO")
