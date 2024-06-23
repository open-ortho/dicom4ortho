# dicom4ortho/pacs.py

import pydicom
from pynetdicom import AE, StoragePresentationContexts
import requests
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger()

def send_to_pacs_dimse(dicom_files, pacs_ip, pacs_port, pacs_aet):
    """Send multiple DICOM files to PACS using DIMSE protocol."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    # Create application entity and specify the requested presentation contexts
    ae = AE()
    ae.requested_contexts = StoragePresentationContexts

    # Establish association with PACS
    assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_aet)
    status = None
    if assoc.is_established:
        for dicom_file_path in dicom_files:
            dataset = pydicom.dcmread(dicom_file_path)
            status = assoc.send_c_store(dataset)
            if status:
                logger.info(f'C-STORE request status: 0x{status.Status:04x}')
            else:
                logger.error('Connection timed out, was aborted, or received an invalid response')

        # Release the association
        assoc.release()
    else:
        logger.error('Failed to establish association')

    # Shut down the AE to clean up resources
    ae.shutdown()
    return status

def send_to_pacs_wado(dicom_file_path, dicomweb_url, username=None, password=None):
    """Send DICOM file to PACS using WADO/DICOMweb."""
    dataset = pydicom.dcmread(dicom_file_path)
    dicom_bytes = dataset.to_bytes()

    headers = {'Content-Type': 'application/dicom'}
    auth = HTTPBasicAuth(username, password) if username and password else None

    response = requests.post(dicomweb_url, headers=headers, data=dicom_bytes, auth=auth)

    if response.status_code in [200, 204]:
        logger.info('DICOM instance successfully stored.')
    else:
        logger.error(f'Failed to store DICOM instance. Status code: {response.status_code}')
        logger.error(f'Response: {response.text}')
