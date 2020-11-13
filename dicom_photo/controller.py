"""
Controller
"""
import os
import os.path
import csv
import datetime
import logging
import dicom_photo.model as model

import dicom_photo.defaults as defaults

class SimpleController(object):
    """
    Simple Controller
    """

    def __init__(self, args):
        self._cli_args = args
        self.photo = None

    def bulk_convert_from_csv(self, csv_input):
        with open(csv_input, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row['image_filename'] =\
                os.path.join(os.path.dirname(csv_input),row['image_filename'])
                self.convert_image_to_dicom_photograph(metadata=row)


    def convert_image_to_dicom_photograph(self, metadata):
        ''' Converts a plain image into a DICOM object.

        All image metadata are passed as a dict in metadata with the following keys:

        image_filename: Input image file name

        output_image_filename: the filename of the output .DCM image. You must
        provide your extension here.

        patient_firstname

        patient_lastname

        patient_id

        patient_sex

        patient_birthdate

        dental_provider_firstname

        dental_provider_lastname
        '''

        if ('output_image_filename' not in metadata) or (metadata['output_image_filename'] is None):
            outputfilename = metadata['image_filename'].replace(metadata['image_filename'].split('.')[-1],'dcm')
        else:
            outputfilename = metadata['output_image_filename']
            
        self.photo = model.OrthodonticPhotograph(
            photo_type = metadata['image_type'], 
            input_image_filename = metadata['image_filename'],
            output_image_filename = outputfilename)
            
        self.photo.study_instance_uid = metadata['study_instance_uid']
        self.photo.series_instance_uid = metadata['series_instance_uid']
        self.photo.patient_firstname = metadata['patient_firstname']
        self.photo.patient_lastname = metadata['patient_lastname']
        self.photo.patient_id = metadata['patient_id']
        self.photo.patient_sex = metadata['patient_sex']
        self.photo.patient_birthdate = datetime.datetime.strptime(metadata['patient_birthdate'], defaults.IMPORT_DATE_FORMAT).date()
        self.photo.dental_provider_firstname = metadata['dental_provider_firstname']
        self.photo.dental_provider_lastname = metadata['dental_provider_lastname']
        self.photo.equipment_manufacturer = metadata['manufacturer']

        self.photo.set_image()
        self.photo.save_implicit_little_endian()

    # def convert_image_to_dicom_photograph(
    #     self,
    #     image_type, 
    #     input_image_filename, 
    #     output_image_filename):
        
    #     self.photo.set_image(filename=input_image_filename)
    #     self.photo.save_implicit_little_endian(output_image_filename)

    def validate_dicom_file(self,input_image_filename):
        ''' Validate DICOM File.

        Requires installation of dicom3tools.
        '''

        self.print_dicom_file(input_image_filename)
        print('\nValidating file {}'.format(input_image_filename))
        dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
        os.system('{} {}'.format(
            os.path.join(dicom3tools_path,'dciodvfy'),
            input_image_filename))


    def print_dicom_file(self,input_image_filename):
        ''' Print DICOM tags
        '''
        _photo = model.DicomBase(
            input_image_filename = input_image_filename,
            output_image_filename = None)
        _photo.load(input_image_filename)
        _photo.print()

