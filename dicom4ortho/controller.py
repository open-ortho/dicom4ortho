"""
Controller
"""
import os
import os.path
import csv
import datetime
import pathlib
import dicom4ortho.model as model

# Just importing will do to execute the code in the module. Pylint will
# complain though.
# pylint: disable=unused-import
import dicom4ortho.m_dental_acquisition_context_module

import dicom4ortho.defaults as defaults
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph

class SimpleController(object):
    """
    Simple Controller
    """

    def __init__(self, args):
        self._cli_args = args
        self.photo = None

    def bulk_convert_from_csv(self, csv_input, teeth=None):
        with open(csv_input, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row['input_image_filename'] =\
                    os.path.join(os.path.dirname(csv_input),
                                 row['input_image_filename'])
                row['teeth'] = teeth
                self.convert_image_to_dicom4orthograph(metadata=row)

    def convert_image_to_dicom4orthograph(self, metadata):
        ''' Converts a plain image into a DICOM object.

        All image metadata are passed as a dict in metadata with the following keys:

        input_image_filename: Input image file name

        output_image_filename: the filename of the output .DCM image. You must
        provide your extension here.

        metadata:

            patient_firstname           :
            patient_lastname            :
            patient_id                  :
            patient_sex                 :
            patient_birthdate           :
            dental_provider_firstname   :
            dental_provider_lastname    :
            teeth                       : array of teeth visible in the photograph.
                                          Use ISO notation in string. Example:
                                          teeth=['24','25','26','27','28','34','35','36','37','38']
            output_image_filename       : filename to write dicom image into.
                                          Default is the same name as the input file name with replaced
                                          extension.
        '''

        if ('output_image_filename' not in metadata) or (metadata['output_image_filename'] is None):
            p = pathlib.Path(metadata['input_image_filename'])
            metadata['output_image_filename'] = str(p.with_suffix('.dcm'))

        self.photo = OrthodonticPhotograph(**metadata)

        self.photo.study_instance_uid = metadata['study_instance_uid']
        self.photo.study_description = metadata['study_description']
        self.photo.series_instance_uid = metadata['series_instance_uid']
        self.photo.series_description = metadata['series_description']
        self.photo.patient_firstname = metadata['patient_firstname']
        self.photo.patient_lastname = metadata['patient_lastname']
        self.photo.patient_id = metadata['patient_id']
        self.photo.patient_sex = metadata['patient_sex']
        self.photo.patient_birthdate = datetime.datetime.strptime(
            metadata['patient_birthdate'], defaults.IMPORT_DATE_FORMAT).date()
        self.photo.dental_provider_firstname = metadata['dental_provider_firstname']
        self.photo.dental_provider_lastname = metadata['dental_provider_lastname']
        self.photo.equipment_manufacturer = metadata['manufacturer']

        # TODO: check if metadata['teeth'] contains teeth and add
        # What teeth are shown in the images is something we cannot guess from
        # what image type is taken, and shold be entered manually or
        # automtaicaly by the implementing software. Therefore, i would like
        # the controller to have an option to add teeth and provide this option
        # to the end user which, in this case, is the CLI, and the CSV import
        # file.
        # if metadata['teeth']

        self.photo.set_image()
        self.photo.save_implicit_little_endian()

    # def convert_image_to_dicom4orthograph(
    #     self,
    #     image_type,
    #     input_image_filename,
    #     output_image_filename):

    #     self.photo.set_image(filename=input_image_filename)
    #     self.photo.save_implicit_little_endian(output_image_filename)

    def validate_dicom_file(self, input_image_filename):
        ''' Validate DICOM File.

        Requires installation of dicom3tools.
        '''

        self.print_dicom_file(input_image_filename)
        print('\nValidating file {}'.format(input_image_filename))
        dicom3tools_path = '/usr/local/opt/dicom3tools'
        os.system('{} {}'.format(
            os.path.join(dicom3tools_path, 'dciodvfy'),
            input_image_filename))

    def print_dicom_file(self, input_image_filename):
        ''' Print DICOM tags
        '''
        _photo = model.DicomBase(
            input_image_filename=input_image_filename,
            output_image_filename=None)
        _photo.load(input_image_filename)
        _photo.print()
