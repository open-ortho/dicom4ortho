""" dicom/dimse: functionality to interact with the DICOM DIMSE protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""
from pydicom.uid import ImplicitVRLittleEndian
from pydicom import dcmread
from pynetdicom import AE, StoragePresentationContexts
import logging

from dicom4ortho.defaults import PROJECT_NAME

logger = logging.getLogger(__name__)


def send(dicom_files, pacs_ip, pacs_port, pacs_aet):
    """Send multiple DICOM files to PACS using DIMSE protocol.
    
    
    """
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
