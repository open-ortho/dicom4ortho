"""
Controller
"""
import os
import csv
from pathlib import Path
from pydicom.dataset import Dataset

from dicom4ortho.config import DICOM3TOOLS_PATH
from dicom4ortho.model import DicomBase
from dicom4ortho.m_dent_oip import DENT_OIP
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph, OrthodonticSeries
from dicom4ortho.dicom import wado, dimse

import logging
logger = logging.getLogger(__name__)

class OrthodonticController(object):
    """ Controller

    """

    def __init__(self, **kwargs):
        """
            allowed arguments for constructor:

            url_codes:  location of file that contains the codes used in the views.
                        Format is a URL, so file:/// for local files, https://, etc. 
                        If not set, the internal one (downloaded from the dent-oip profile) will be used.

            url_views:  location of file that contains the views used for each keyword.
                        Format is a URL, so file:/// for local files, https://, etc.
                        If not set, the internal one (downloaded from the dent-oip profile) will be used.
        """
        self.photo = None
        self.dent_oip = DENT_OIP(
            url_codes=kwargs.get('url_codes'),
            url_views=kwargs.get('url_views'))

    def bulk_convert_from_csv(self, csv_input):
        with open(csv_input, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row['input_image_filename'] = (
                    Path(csv_input).parent / row['input_image_filename'])
                self.convert_image_to_dicom4orthograph_and_save(metadata=row)

    def convert_image_to_dicom4orthograph(self, metadata) -> OrthodonticPhotograph:
        ''' Converts a plain image into a DICOM object.

        All image metadata are passed as a dict in metadata with the following keys:

        metadata:

            input_image_filename        : Input image file name
            patient_firstname           :
            patient_lastname            :
            patient_id                  :
            patient_sex                 :
            patient_birthdate           :
            dental_provider_firstname   :
            dental_provider_lastname    :
            treatment_event_type        : Allowed values:
                                            - "PatientRegistration"
                                            - "OrthodonticTreatment"
                                            - "Posttreatment"
            days_after_event            : number of days from treatment_event_type
            burned_in_annotation        : 'YES' or 'NO'. Default = 'NO'.
            output_image_filename       : filename to write dicom image into.
                                          Default is the same name as the input file name with replaced
                                          extension.
        '''

        if ('output_image_filename' not in metadata) or (metadata['output_image_filename'] is None):
            p = Path(metadata['input_image_filename'])
            metadata['output_image_filename'] = str(p.with_suffix('.dcm'))

        self.photo = OrthodonticPhotograph(**metadata)

        return self.photo

    def convert_image_plus_mwl_to_dicom4orthograph(self, image_bytes, mwl:Dataset) -> OrthodonticPhotograph:
        ''' Converts a PIL image into an OrthodonticPhotograph using a DICOM MWL for metadata.

        The MWL is passed as a pydicom Dataset object, and should contain a single ScheduledProtocolCode.

        Parameters:
        image_bytes (bytes): Image bytes. Purposely set to raw bytes to avoid file I/O. Purposely avoiding PIL Image, because once in PIL Image, the image will be decoded and re-encoded even when saved as JPEG. This would result in loss of image quality.

        mwl (Dataset): DICOM MWL object.

        '''
        metadata = {
            'input_image_filename': None,
            'input_image_bytes': image_bytes,
            'dicom_mwl': mwl,
        }
        self.photo = OrthodonticPhotograph(**metadata)
        pass

    def convert_image_to_dicom4orthograph_and_save(self, metadata):
        _photo = self.convert_image_to_dicom4orthograph(metadata=metadata)
        _photo.save()

    def convert_images_to_orthodontic_series(self, images, metadata) -> OrthodonticSeries:
        """ Convert a list of Images and metadata into an OrthodonticSeries containing OrthodonticPhotographs.
        """
        orthodontic_series = OrthodonticSeries()
        for image in images:
            metadata['input_image_filename'] = image
            orthodontic_photograph = OrthodonticPhotograph(**metadata)
            orthodontic_series.add(orthodontic_photograph)
        return orthodontic_series

    def validate_dicom_file(self, input_image_filename=None):
        ''' Validate DICOM File.

        Requires installation of dicom3tools.
        '''

        if input_image_filename is None:
            input_image_filename = self.photo.output_image_filename

        self.print_dicom_file(input_image_filename)
        logger.info('\nValidating file %s', input_image_filename)
        os.system('{} {}'.format(
            Path(DICOM3TOOLS_PATH, 'dciodvfy'),
            input_image_filename))

    def print_dicom_file(self, input_image_filename):
        ''' Print DICOM tags
        '''
        _photo = DicomBase(
            input_image_filename=input_image_filename,
            output_image_filename=None)
        _photo.load(input_image_filename)
        _photo.print()

    def send(self, send_method, **kwargs):
        """
        Send DICOM files to a PACS.

        Parameters:
        orthodontic_series (OrthodonticSeries): a dicom4ortho.m_orthodontic_photograph.OrthodonticSeries
        dicom_files (str): Array of paths to the DICOM files to send.
        dicom_datasets (List[Dataset]): List of pydicom Dataset objects to send.
        send_method (str): Method to send DICOM. Must be 'dimse' or 'wado'.
        **kwargs: Additional keyword arguments depending on the send method:

            For send_method 'dimse':
                pacs_dimse_hostname (str): IP address of the PACS server.
                pacs_dimse_port (int): Port of the PACS server.
                pacs_dimse_aet (str): AE Title of the PACS server.

            For send_method 'wado':
                pacs_wado_url (str): URL of the DICOMweb server.
                pacs_wado_username (str, optional): Username for DICOMweb authentication.
                pacs_wado_password (str, optional): Password for DICOMweb authentication.

        Raises:
        ValueError: If an invalid send method is specified or required kwargs are missing.

        Examples:
        send(
            dicom_files=['path/to/output.dcm'],
            send_method='dimse',
            pacs_dimse_hostname='127.0.0.1',
            pacs_dimse_port=104,
            pacs_dimse_aet='PACS_AET'
        )

        send(
            orthodontic_series=orthodontic_series,
            send_method='wado',
            pacs_wado_url='http://dicomweb-server.com/dicomweb/studies',
            pacs_wado_username='user',
            pacs_wado_password='pass'
        )

        send(
            dicom_datasets=[ds1, ds2],
            send_method='dimse',
            pacs_dimse_hostname='127.0.0.1',
            pacs_dimse_port=104,
            pacs_dimse_aet='PACS_AET'
        )

        Returns either a DICOM Dateset or a response containing the response.
        """

        # Convert image to DICOM (assuming you have a function for this)

        # Send the DICOM file based on the specified method
        if send_method == 'dimse':
            return dimse.send(
                dicom_datasets=kwargs.get('dicom_datasets', None),
                dicom_files=kwargs.get('dicom_files', None),
                orthodontic_series=kwargs.get('orthodontic_series', None),
                pacs_dimse_hostname=kwargs['pacs_dimse_hostname'],
                pacs_dimse_port=kwargs['pacs_dimse_port'],
                pacs_dimse_aet=kwargs['pacs_dimse_aet'])

        elif send_method == 'wado':
            return wado.send(
                dicom_files=kwargs.get('dicom_files', None),
                orthodontic_series=kwargs.get('orthodontic_series', None),
                pacs_wado_url=kwargs['pacs_wado_url'],
                pacs_wado_username=kwargs.get('pacs_wado_username'),
                pacs_wado_password=kwargs.get('pacs_wado_password'),
                ssl_certificate=kwargs.get('ssl_certificate'),
                ssl_verify=kwargs.get('ssl_verify'),
            )
        else:
            logger.error('Invalid send method specified.')


    def get_image_view_code(self, ds:Dataset, code_system):
        pass