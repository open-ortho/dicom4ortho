# dicom4ortho/pacs.py

import io
import sys
import uuid
from pathlib import Path
from pydicom.uid import ImplicitVRLittleEndian, ExplicitVRLittleEndian
from pydicom import dcmread, dataset, dcmwrite
from pynetdicom import AE, StoragePresentationContexts, sop_class
import requests
from requests.auth import HTTPBasicAuth
import logging

from dicom4ortho.defaults import PROJECT_NAME

logger = logging.getLogger()


def send_to_pacs_dimse(dicom_files, pacs_ip, pacs_port, pacs_aet):
    """Send multiple DICOM files to PACS using DIMSE protocol."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    # Create application entity and specify the requested presentation contexts
    ae = AE(ae_title=PROJECT_NAME.upper())
    ae.requested_contexts = StoragePresentationContexts

    # Establish association with PACS
    assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_aet)
    status = None
    if assoc.is_established:
        for dicom_file_path in dicom_files:
            dataset = dcmread(dicom_file_path)

            # Set TransferSyntax to something common. This is done at the dicom instance itself.
            if not hasattr(dataset, 'file_meta') or dataset.file_meta is None:
                dataset.file_meta = dataset.FileMetaDataset()
            dataset.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
            dataset.is_implicit_VR = True
            dataset.is_little_endian = True

            status = assoc.send_c_store(dataset)
            if status:
                logger.info(f'C-STORE request status: 0x{status.Status:04x}')
            else:
                logger.error(
                    'Connection timed out, was aborted, or received an invalid response')

        # Release the association
        assoc.release()
    else:
        logger.error('Failed to establish association')

    # Shut down the AE to clean up resources
    ae.shutdown()
    return status


def send_to_pacs_wado(dicom_files, dicomweb_url, username=None, password=None):
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

    