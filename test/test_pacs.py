# tests/test_pacs.py
# 
# These tests are not real tests. They are mostly here to serve as examples for usage. Should probably go in examples.
#

import os
import unittest
from unittest.mock import patch, MagicMock
from pynetdicom import AE
from requests.auth import HTTPBasicAuth
from dicom4ortho import pacs
import logging
logging.basicConfig(level=logging.INFO)


class TestPacsModule(unittest.TestCase):

    def test_send_to_pacs_dimse(self):
        # Arrange
        BASE_PATH = os.path.dirname(__file__)
        dicom_file_path = os.path.join(BASE_PATH, 'resources', 'test.dcm')
        pacs_ip = '192.168.2.86'
        pacs_port = 104
        pacs_aet = 'OVENA-DEV'

        status = pacs.send_to_pacs_dimse([dicom_file_path], pacs_ip, pacs_port, pacs_aet)
        self.assertEqual(status.Status,0)

    @patch('pydicom.dcmread')
    @patch('requests.post')
    def test_send_to_pacs_wado(self, mock_post, mock_dcmread):
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
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Act
        pacs.send_to_pacs_wado(dicom_file_path, dicomweb_url, username, password)

        # Assert
        mock_dcmread.assert_called_once_with(dicom_file_path)
        mock_post.assert_called_once_with(
            dicomweb_url,
            headers={'Content-Type': 'application/dicom'},
            data=b'dicom-bytes',
            auth=HTTPBasicAuth(username, password)
        )

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
        pacs.send_to_pacs_wado(dicom_file_path, dicomweb_url, username, password)

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
