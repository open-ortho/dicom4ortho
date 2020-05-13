"""
Controller
"""
import dicom_photo.model as model

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
        
        self.dicom_photograph.set_image()
    