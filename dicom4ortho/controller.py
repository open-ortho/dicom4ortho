"""
Controller
"""
import os
import csv
import datetime
from pathlib import Path
import dicom4ortho.model as model

import dicom4ortho.defaults as defaults
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph

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

    def convert_image_to_dicom4orthograph(self, metadata):
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

        self.photo.save()

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
