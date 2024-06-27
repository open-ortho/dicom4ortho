""" dicom/dimse: functionality to interact with the DICOM DIMSE protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""
import logging
from pydicom.uid import ImplicitVRLittleEndian
from pydicom import dcmread
from pynetdicom import AE, StoragePresentationContexts

from dicom4ortho.defaults import PROJECT_NAME

logger = logging.getLogger(__name__)


def send(**kwargs):
    """ Send multiple DICOM files to PACS using DIMSE protocol.

    kwargs:
        dicom_files (List[str]): List of DICOM files.
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        pacs_ip (str): IP address of the PACS server.
        pacs_port (int): Port of the PACS server.
        pacs_aet (str): AE Title of the PACS server.

    """
    orthodontic_series = kwargs.get('orthodontic_series', None)
    if orthodontic_series:
        raise NotImplementedError(
            "dimse.send() with OrthodonticSeries is not yet implemented. Use dicom_files")

    dicom_files = kwargs.get('dicom_files', None)
    if not dicom_files:
        logger.error("No files to send to. Set the dicom_files argument.")
        return None

    pacs_ip = kwargs.get('pacs_ip', None)
    if not pacs_ip:
        logger.error("Nowhere to send to. Set the pacs_ip argument.")
        return None

    pacs_port = kwargs.get('pacs_port', None)
    if not pacs_port:
        logger.error("No PACS Port defined! Set the pacs_port argument.")
        return None

    pacs_aet = kwargs.get('pacs_aet', None)
    if not pacs_aet:
        logger.error(
            "No PACS Application Entity Title defined! Set the pacs_aet argument.")
        return None

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
