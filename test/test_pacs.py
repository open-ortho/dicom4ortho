# tests/test_pacs.py
#
# 
#

import os
import unittest
from pprint import pprint
from pathlib import Path
from unittest.mock import patch, MagicMock
from pynetdicom import AE
from requests.auth import HTTPBasicAuth
from dicom4ortho import pacs

import logging
logging.basicConfig(level=logging.INFO)


class TestPacsModule(unittest.TestCase):
    def setUp(self) -> None:
        self.BASE_PATH = os.path.dirname(__file__)
        self.dicom_file_path = os.path.join(
            self.BASE_PATH, 'resources', 'test.dcm')
        return super().setUp()

    def test_send_to_pacs_dimse(self):
        # Arrange
        # dicom_file_path = Path(
        #     '/Users/afm/Desktop/1141_SLOT_1/PAZIENTE_1/DSC_0001.DCM')
        # dicom_file_path = Path('/Users/afm/git/open-ortho/dicom4ortho/test/resources/d90.dcm')
        pacs_ip = '127.0.0.1'
        pacs_port = 4242
        pacs_aet = 'ORTHANC-MOCK'

        status = pacs.send_to_pacs_dimse(
            [self.dicom_file_path], pacs_ip, pacs_port, pacs_aet)
        if status:
            self.assertEqual(status.Status, 0)
        else:
            print("WARNING: No response from PACS. Skipping test.")

    def test_send_to_pacs_wado(self):
        """
        Test written by ChatGPT, but i have not actually tested it: It wrote both the test and the function, so they could both be wrong.
        """
        # Arrange
        dicomweb_url = 'http://127.0.0.1:8201/dicom-web/studies'
        username = 'orthanc'
        password = 'mock'


        # Act
        response = pacs.send_to_pacs_wado(
            self.dicom_file_path, dicomweb_url, username, password)

        self.assertEqual(response.status_code,200)
        # pprint(response.json())

    @patch('pydicom.dcmread')
    @patch('requests.post')
    def test_send_to_pacs_wado_failure(self, mock_post, mock_dcmread):
        """
        Test written by ChatGPT, but i have not actually tested it: It wrote both the test and the function, so they could both be wrong.
        """
        # Arrange
        dicom_file_path = 'test.dcm'
        dicomweb_url = 'http://dicomweb-server.com/dicomweb/studies'
        username = 'username'
        password = 'password'

        dataset = MagicMock()
        dataset.to_bytes.return_value = b'dicom-bytes'
        mock_dcmread.return_value = dataset

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # Act
        pacs.send_to_pacs_wado(
            dicom_file_path, dicomweb_url, username, password)

        # Assert
        mock_dcmread.assert_called_once_with(dicom_file_path)
        mock_post.assert_called_once_with(
            dicomweb_url,
            headers={'Content-Type': 'application/dicom'},
            data=b'dicom-bytes',
            auth=HTTPBasicAuth(username, password)
        )


if __name__ == '__main__':
    unittest.main()
