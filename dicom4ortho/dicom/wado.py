""" dicom/wado: functionality to interact with the DICOM protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""

from typing import cast
import tempfile
import uuid
import logging
import requests
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph

logger = logging.getLogger(__name__)


def send(**kwargs):
    """ send images or OrthodonticSeries to PACS using STOW-RS.

    Has the ability to provide a PEM certificate to validate the connection, for self signed https connections. The PEM is fed via the ssl_certificate as a string, to facilitate storage in configurations.
    
    kwargs:
        dicomweb_url (str): URL of the DICOMweb server.
        dicom_files (List[str]): List of DICOM files.
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        username (str, optional): Username for DICOMweb authentication.
        password (str, optional): Password for DICOMweb authentication.
        ssl_certificate (str, optional): SSL Certificate to use to validate SSL Connection in string format.

    Inspired by:
    https://orthanc.uclouvain.be/hg/orthanc-dicomweb/file/default/Resources/Samples/Python/SendStow.py

    as suggested by Orthanc Dicomweb Plugin book:
    https://orthanc.uclouvain.be/book/plugins/dicomweb.html#id19


    """
    dicomweb_url = kwargs.get('dicomweb_url')
    if not dicomweb_url:
        logger.error(
            "No URL to send to. Specify a dicom-web URL using the dicomweb_url argument.")
        return None

    boundary = str(uuid.uuid4())
    parts = []

    # Prepare content
    def add_content(content): return (
        f"--{boundary}\r\n"
        "Content-Type: application/dicom\r\n"
        f"Content-Length: {len(content)}\r\n\r\n"
    ).encode('ascii') + content + b"\r\n"

    dicom_files = kwargs.get('dicom_files', [])
    orthodontic_series = kwargs.get('orthodontic_series')
    ssl_certificate = kwargs.get('ssl_certificate')

    if dicom_files:
        for dicom_file in dicom_files:
            try:
                with open(dicom_file, 'rb') as f:
                    parts.append(add_content(f.read()))
            except Exception as e:
                logger.error('Error processing file %s: %s',
                             dicom_file, str(e))
    elif orthodontic_series:
        for photo in orthodontic_series:
            photo = cast(OrthodonticPhotograph, photo)
            parts.append(add_content(photo.to_byte().getvalue()))
    else:
        logger.error(
            "No data to send. Specify either dicom_files or orthodontic_series.")
        return None

    # Finalize the multipart body
    parts.append(f"--{boundary}--".encode('ascii'))
    body = b''.join(parts)

    # Send request
    headers = {
        'Content-Type': f'multipart/related; type="application/dicom"; boundary={boundary}',
        'Accept': 'application/dicom+json',
    }
    auth = (kwargs.get('username'), kwargs.get('password')) if kwargs.get(
        'username') and kwargs.get('password') else None

    if ssl_certificate:
        # post(verify=) take a filename as string. So we have to write to a tmpfile.
        with tempfile.NamedTemporaryFile(suffix='.pem', mode='w+') as tmpfile:
            tmpfile.write(ssl_certificate)
            tmpfile.flush()  # Ensure data is written to the file before it's read by the requests library

            # Now perform the POST request within the 'with' block
            response = requests.post(dicomweb_url, data=body,
                                     headers=headers, auth=auth, verify=tmpfile.name)
    else:
        response = requests.post(dicomweb_url, data=body,
                                 headers=headers, auth=auth)

    return response
