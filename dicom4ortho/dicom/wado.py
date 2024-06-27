""" dicom/wado: functionality to interact with the DICOM protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""

from typing import cast
import uuid
import requests
from requests.auth import HTTPBasicAuth
import logging
from dicom4ortho.m_orthodontic_photograph import OrthodonticSeries, OrthodonticPhotograph

logger = logging.getLogger(__name__)


def old_send(dicom_files, dicomweb_url, username=None, password=None):
    """ Create a multipart message whose body contains all the input DICOM files

    kwargs:
        dicomweb_url (str): URL of the DICOMweb server.
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        username (str, optional): Username for DICOMweb authentication.
        password (str, optional): Password for DICOMweb authentication.


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


def send(**kwargs):
    """ send images or OrthodonticSeries to PACS using STOW-RS.

    kwargs:
        dicomweb_url (str): URL of the DICOMweb server.
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        username (str, optional): Username for DICOMweb authentication.
        password (str, optional): Password for DICOMweb authentication.


    Inspired by:
    https://orthanc.uclouvain.be/hg/orthanc-dicomweb/file/default/Resources/Samples/Python/SendStow.py

    as suggested by Orthanc Dicomweb Plugin book:
    https://orthanc.uclouvain.be/book/plugins/dicomweb.html#id19

    
    """
    dicomweb_url = kwargs.get('dicomweb_url')
    if not dicomweb_url:
        logger.error("No URL to send to. Specify a dicom-web URL using the dicomweb_url argument.")
        return None

    boundary = str(uuid.uuid4())
    parts = []

    # Prepare content
    add_content = lambda content: (
        f"--{boundary}\r\n"
        "Content-Type: application/dicom\r\n"
        f"Content-Length: {len(content)}\r\n\r\n"
    ).encode('ascii') + content + b"\r\n"

    dicom_files = kwargs.get('dicom_files', [])
    orthodontic_series = kwargs.get('orthodontic_series')

    if dicom_files:
        for dicom_file in dicom_files:
            try:
                with open(dicom_file, 'rb') as f:
                    parts.append(add_content(f.read()))
            except Exception as e:
                logger.error('Error processing file %s: %s', dicom_file, str(e))
    elif orthodontic_series:
        for photo in orthodontic_series:
            parts.append(add_content(photo.to_byte().getvalue()))
    else:
        logger.error("No data to send. Specify either dicom_files or orthodontic_series.")
        return None

    # Finalize the multipart body
    parts.append(f"--{boundary}--".encode('ascii'))
    body = b''.join(parts)

    # Send request
    headers = {
        'Content-Type': f'multipart/related; type="application/dicom"; boundary={boundary}',
        'Accept': 'application/dicom+json',
    }
    auth = (kwargs.get('username'), kwargs.get('password')) if kwargs.get('username') and kwargs.get('password') else None
    response = requests.post(dicomweb_url, data=body, headers=headers, auth=auth)
    return response
