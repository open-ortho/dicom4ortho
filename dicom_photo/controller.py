"""
Controller
"""
import dicom_photo.model as model
import logging
import os

class SimpleController(object):
    """
    Simple Controller
    """

    def __init__(self, args):
        self.photo = model.PhotographBase()
        self.photo.input_image_filename = args.input_filename
        self.photo.output_image_filename = args.output_filename

        self.photo.set_dataset()

    def convert_image_to_dicom_photograph(
        self,
        image_type, 
        input_image_filename, 
        output_image_filename):
        
        self.photo.set_image(filename=input_image_filename)
        self.photo.save_explicit_big_endian(output_image_filename)

    def validate_dicom(self,input_image_filename):
        print('\nValidating file {}'.format(input_image_filename))
        dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
        os.system('{} {}'.format(
            os.path.join(dicom3tools_path,'dciodvfy'),
            input_image_filename))
