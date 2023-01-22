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

    def test_load_image_types(self):
        controller.SimpleController(None)
        self.assertEqual(len(defaults.image_types), 73)
        self.assertEqual(len(defaults.image_types['EV01']), 2)
        self.assertEqual(defaults.image_types['EV01'][0], "EO.RP.LR.CO")
        self.assertEqual(defaults.image_types['EV04'][1], "Extraoral, Right Profile (subject is facing observer's right), Lips Closed, Centric Relation")
