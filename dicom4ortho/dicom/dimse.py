""" dicom/dimse: functionality to interact with the DICOM DIMSE protocol.

This module is here to satisfy specificion  **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).

"""
from dicom4ortho import logger
from pynetdicom.sop_class import VLPhotographicImageStorage  # pylint: disable=E0611
from pydicom.dataset import Dataset
from pydicom import dcmread
from pynetdicom import AE

from dicom4ortho.config import PROJECT_NAME
from pydicom.uid import AllTransferSyntaxes, ImplicitVRLittleEndian


def send(**kwargs) -> Dataset:
    """ Send multiple DICOM files to PACS using DIMSE protocol.

    kwargs:
        dicom_files (List[str]): List of DICOM files.
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        pacs_dimse_hostname (str): IP address of the PACS server.
        pacs_dimse_port (int): Port of the PACS server.
        pacs_dimse_aet (str): AE Title of the PACS server.
        local_aet (str): Local AE Title to use (default: PROJECT_NAME.upper()).

    returns a Status Dataset contiaining the response.
    """
    orthodontic_series = kwargs.get('orthodontic_series', None)
    if orthodontic_series:
        raise NotImplementedError(
            "dimse.send() with OrthodonticSeries is not yet implemented. Use dicom_files")

    dicom_datasets = kwargs.get('dicom_datasets', None)
    dicom_files = kwargs.get('dicom_files', None)
    if not dicom_datasets and not dicom_files:
        logger.error(
            "No files or DICOM Datasets to send to. Set the dicom_files or dicom_datasets argument.")
        return None

    pacs_dimse_hostname = kwargs.get('pacs_dimse_hostname', None)
    if not pacs_dimse_hostname:
        logger.error(
            "Nowhere to send to. Set the pacs_dimse_hostname argument.")
        return None

    pacs_dimse_port = kwargs.get('pacs_dimse_port', None)
    if not pacs_dimse_port:
        logger.error("No PACS Port defined! Set the pacs_dimse_port argument.")
        return None

    pacs_dimse_aet = kwargs.get('pacs_dimse_aet', None)
    if not pacs_dimse_aet:
        logger.error(
            "No PACS Application Entity Title defined! Set the pacs_dimse_aet argument.")
        return None

    local_aet = kwargs.get('local_aet', PROJECT_NAME.upper())

    # Create application entity and specify the requested presentation contexts
    ae = AE(ae_title=local_aet)

    # Add all transfer syntaxes to the VLPhotographicImageStorage.
    for transfer_syntax in AllTransferSyntaxes:
        ae.add_requested_context(VLPhotographicImageStorage, transfer_syntax)

    # Now try to establish the association with this comprehensive list of presentation contexts
    assoc = ae.associate(
        addr=pacs_dimse_hostname,
        port=pacs_dimse_port,
        ae_title=pacs_dimse_aet)

    status = None
    if assoc.is_established:
        combined_dicoms = (dicom_files or []) + (dicom_datasets or [])
        for dicom_thing in combined_dicoms:
            logger.debug('Sending dicom Dataset')
            if isinstance(dicom_thing, Dataset):
                dataset = dicom_thing
            else:
                dataset = dcmread(dicom_thing)

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
                    f'Connection timed out, was aborted, or received an invalid response. Status: [{status}]')

        # Release the association
        assoc.release()
    else:
        logger.error('Failed to establish association')

    # Shut down the AE to clean up resources
    ae.shutdown()
    return status
