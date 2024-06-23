"""
Controller
"""
import os
import csv
import datetime
from pathlib import Path

import dicom4ortho.defaults as defaults
import dicom4ortho.model as model
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.pacs import send_to_pacs_dimse, send_to_pacs_wado

class SimpleController(object):
    """
    Simple Controller
    """

    photo = OrthodonticPhotograph()

    def __init__(self, args=None):
        self._cli_args = args
        self.photo = None

    def bulk_convert_from_csv(self, csv_input, teeth=None):
        with open(csv_input, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row['input_image_filename'] = (Path(csv_input).parent / row['input_image_filename'])
                row['teeth'] = teeth
                self.convert_image_to_dicom4orthograph(metadata=row)

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
            teeth                       : array of teeth visible in the photograph.
                                          Use ISO notation in string. Example:
                                          teeth=['24','25','26','27','28','34','35','36','37','38']
            output_image_filename       : filename to write dicom image into.
                                          Default is the same name as the input file name with replaced
                                          extension.
        '''

        if ('output_image_filename' not in metadata) or (metadata['output_image_filename'] is None):
            p = Path(metadata['input_image_filename'])
            metadata['output_image_filename'] = str(p.with_suffix('.dcm'))

        self.photo = OrthodonticPhotograph(**metadata)

        # TODO: check if metadata['teeth'] contains teeth and add
        # What teeth are shown in the images is something we cannot guess from
        # what image type is taken, and shold be entered manually or
        # automtaicaly by the implementing software. Therefore, i would like
        # the controller to have an option to add teeth and provide this option
        # to the end user which, in this case, is the CLI, and the CSV import
        # file.
        # if metadata['teeth']

        return self.photo

    def convert_image_to_dicom4orthograph_and_save(self, metadata):
        _photo = self.convert_image_to_dicom4orthograph(metadata=metadata)
        _photo.save()

    def validate_dicom_file(self, input_image_filename=None):
        ''' Validate DICOM File.

        Requires installation of dicom3tools.
        '''

        if input_image_filename is None:
            input_image_filename = self.photo.output_image_filename

        self.print_dicom_file(input_image_filename)
        print('\nValidating file {}'.format(input_image_filename))
        os.system('{} {}'.format(
            Path(defaults.DICOM3TOOLS_PATH, 'dciodvfy'),
            input_image_filename))

    def print_dicom_file(self, input_image_filename):
        ''' Print DICOM tags
        '''
        _photo = model.DicomBase(
            input_image_filename=input_image_filename,
            output_image_filename=None)
        _photo.load(input_image_filename)
        _photo.print()


    def process_and_send(self, send_method, **kwargs):
        """
        Convert an image to DICOM format and send it to a PACS.

        Parameters:
        image_path (str): Path to the input image.
        dicom_file_path (str): Path to the output DICOM file.
        send_method (str): Method to send DICOM. Must be 'dimse' or 'wado'.
        **kwargs: Additional keyword arguments depending on the send method:
    
            For send_method 'dimse':
                pacs_ip (str): IP address of the PACS server.
                pacs_port (int): Port of the PACS server.
                pacs_aet (str): AE Title of the PACS server.

            For send_method 'wado':
                dicomweb_url (str): URL of the DICOMweb server.
                username (str, optional): Username for DICOMweb authentication.
                password (str, optional): Password for DICOMweb authentication.
    
        Raises:
        ValueError: If an invalid send method is specified or required kwargs are missing.
    
        Example:
        process_and_send(
            image_path='path/to/image.jpg',
            dicom_file_path='path/to/output.dcm',
            send_method='dimse',
            pacs_ip='127.0.0.1',
            pacs_port=104,
            pacs_aet='PACS_AET'
        )

        process_and_send(
            image_path='path/to/image.jpg',
            dicom_file_path='path/to/output.dcm',
            send_method='wado',
            dicomweb_url='http://dicomweb-server.com/dicomweb/studies',
            username='user',
            password='pass'
        )
        """

        # Convert image to DICOM (assuming you have a function for this)

        # Send the DICOM file based on the specified method
        if send_method == 'dimse':
            send_to_pacs_dimse(dicom_file_path, kwargs['pacs_ip'], kwargs['pacs_port'], kwargs['pacs_aet'])
        elif send_method == 'wado':
            send_to_pacs_wado(dicom_file_path, kwargs['dicomweb_url'], kwargs.get('username'), kwargs.get('password'))
        else:
            print('Invalid send method specified.')
