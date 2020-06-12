"""
Controller
"""
import dicom_photo.model as model
import logging
import os
import os.path
import csv

class SimpleController(object):
    """
    Simple Controller
    """

    def __init__(self, args):
        self.photo = model.PhotographBase()
        self.photo.input_image_filename = args.input_filename
        self.photo.output_image_filename = args.output_filename

        self.photo.set_dataset()

    def bulk_convert_from_csv(self, csv_input):
        with open(csv_input, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row['image_filename'] = os.path.join(os.path.dirname(csv_input),row['image_filename'])
                self.convert_image_to_dicom_photograph(metadata=row)


    def convert_image_to_dicom_photograph(self, metadata):
        self.photo = model.PhotographBase()
        self.photo.input_image_filename = metadata['image_filename']
        self.photo.output_image_filename = metadata['image_filename'].replace(metadata['image_filename'].split('.')[-1],'dcm')

        self.photo.set_dataset()
        self.photo.patient_firstname = metadata['patient_firstname']
        self.photo.patient_lastname = metadata['patient_lastname']
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
        self.print_dicom_file(input_image_filename)
        print('\nValidating file {}'.format(input_image_filename))
        dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
        os.system('{} {}'.format(
            os.path.join(dicom3tools_path,'dciodvfy'),
            input_image_filename))


    def print_dicom_file(self,input_image_filename):
        self.photo.load(input_image_filename)
        self.photo.print()

