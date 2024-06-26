""" dicom/wado: functionality to interact with the DICOM protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""

import uuid
import requests
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)


def send(dicom_files, dicomweb_url, username=None, password=None):
    """ Create a multipart message whose body contains all the input DICOM files

    Copied almost exactly from:
    https://orthanc.uclouvain.be/hg/orthanc-dicomweb/file/default/Resources/Samples/Python/SendStow.py

    as suggested by Orthanc Dicomweb Plugin book:
    https://orthanc.uclouvain.be/book/plugins/dicomweb.html#id19

    This function builds the multipart mostly manually. It should be possible to do this cleaner.

    """

    boundary = str(uuid.uuid4())  # The boundary is a random UUID
    body = bytearray()

    for dicom_file in dicom_files:
        try:
            with open(dicom_file, 'rb') as f:
                content = f.read()
                body += bytearray('--%s\r\n' % boundary, 'ascii')
                body += bytearray('Content-Length: %d\r\n' %
                                  len(content), 'ascii')
                body += bytearray('Content-Type: application/dicom\r\n\r\n', 'ascii')
                body += content
                body += bytearray('\r\n', 'ascii')
        except:
            logger.info('Ignoring directory %s' % dicom_file)

    # Closing boundary

    body += bytearray('--%s--' % boundary, 'ascii')

    # Prepare authentication
    auth = HTTPBasicAuth(username, password) if username and password else None

    headers = {
        'Content-Type': 'multipart/related; type="application/dicom"; boundary=%s' % boundary,
        'Accept': 'application/dicom+json',
    }

    # Do the HTTP POST request to the STOW-RS server

    # Use chunked transfer
    # https://2.python-requests.org/en/master/user/advanced/#chunk-encoded-requests
    def gen():
        chunkSize = 1024 * 1024
        l = len(body) // chunkSize
        for i in range(l):
            pos = i * chunkSize
            yield body[pos: pos + chunkSize]
        if len(body) % chunkSize != 0:
            yield body[l * chunkSize:]

    r = requests.post(dicomweb_url, data=gen(), headers=headers, auth=auth)
    return r
