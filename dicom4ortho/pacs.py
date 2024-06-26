# dicom4ortho/pacs.py

import io
import pydicom
from pathlib import Path
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
            dataset = pydicom.dcmread(dicom_file_path)
            
            # Set TransferSyntax to something common. This is done at the dicom instance itself.
            if not hasattr(dataset, 'file_meta') or dataset.file_meta is None:
                dataset.file_meta = pydicom.dataset.FileMetaDataset()
            dataset.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

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

def send_to_pacs_wado(dicom_files, dicomweb_url, username=None, password=None):
    """Send multiple DICOM files to PACS using WADO/DICOMweb."""
    
    # Prepare the files payload for multipart/related
    files = []
    for dicom_file_path in dicom_files:
        # Load and prepare DICOM file
        dataset = pydicom.dcmread(dicom_file_path)
        byte_buffer = io.BytesIO()
        pydicom.dcmwrite(byte_buffer, dataset)
        byte_buffer.seek(0)
        dicom_bytes = byte_buffer.read()

        # Append each file to the files list
        files.append((
            'file', 
            (Path(dicom_file_path).name, dicom_bytes, 'application/dicom')
        ))

    # Prepare authentication
    auth = HTTPBasicAuth(username, password) if username and password else None

    # Send the request with all files
    response = requests.post(dicomweb_url, files=files, auth=auth)

    # Check and log the response
    if response.status_code in [200, 204]:
        logger.info('DICOM instances successfully stored.')
    else:
        logger.error(f'Failed to store DICOM instances. Status code: {response.status_code}')
        logger.error(f'Response: {response.text}')

    return response
