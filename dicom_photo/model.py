"""
The model.
"""
import os
import tempfile
import datetime
import logging

import pydicom
import pynetdicom
from pydicom.dataset import Dataset, FileDataset
from pynetdicom.sop_class import VLPhotographicImageStorage
import pydicom.sequence
import PIL

import dicom_photo.defaults as defaults

class DicomBase(object):
    """
    Functions and fields common to most DICOM images.
    """
    def __init__(
        self, 
        input_image_filename=None,
        output_image_filename=None):
        self.SOPClassUID = VLPhotographicImageStorage
        self.SOPInstanceUID = defaults.generate_dicom_uid()
        self.timeStr = datetime.datetime.now().strftime(defaults.TIME_FORMAT)
        self.dateStr = datetime.datetime.now().strftime(defaults.DATE_FORMAT)
        self.input_image_filename = input_image_filename
        self.output_image_filename = output_image_filename 

    def set_file_meta(self):
        self.file_meta = Dataset()
        self.file_meta.MediaStorageSOPClassUID = self.SOPClassUID
        self.file_meta.MediaStorageSOPInstanceUID = self.SOPInstanceUID
        self.file_meta.ImplementationClassUID = defaults.IMPLEMENTATION_CLASS_UID

    def set_dataset(self,filename=None):
        if self.output_image_filename is None:
            self.output_image_filename = filename
        
        self.ds = FileDataset(
            self.output_image_filename, 
            {},
            file_meta=self.file_meta, 
            preamble=defaults.DICOM_PREAMBLE)

        self.ds.PatientName = "^"
        self.ds.StudyDate = self.dateStr
        self.ds.StudyTime = self.timeStr
        self.ds.SOPClassUID = self.SOPClassUID
        self.ds.SOPInstanceUID = self.SOPInstanceUID

    def set_patient_firstname(self, firstname):
        self.ds.PatientName = "{}^{}".format(
            firstname,
            self.ds.PatientName.split('^')[1])

    def set_patient_lastname(self, lastname):
        self.ds.PatientName = "{}^{}".format(
            lastname,
            self.ds.PatientName.split('^')[0])

    def set_patient_id(self, patient_id):
        self.ds.PatientID = patient_id

    def set_patient_sex(self, patient_sex):
        self.ds.PatientSex = patient_sex

    def set_patient_birthdate(self, patient_birthdate):
        self.ds.PatientBirthDate = patient_birthdate.strftime(defaults.DATE_FORMAT)

    def set_dental_provider_firstname(self,firstname):
        if self.ds.ReferringPhysicianName is None:
            self.ds.ReferringPhysicianName = "^"

        self.ds.ReferringPhysicianName = "{}^{}".format(
            firstname,
            self.ds.ReferringPhysicianName.split('^')[1])

    def set_dental_provider_lastname(self, lastname):
        if self.ds.ReferringPhysicianName is None:
            self.ds.ReferringPhysicianName = "^"
            
        self.ds.PatientName = "{}^{}".format(
            lastname,
            self.ds.ReferringPhysicianName.split('^')[0])


    def set_date_captured(self,date_captured):
        # Date and time are required if images is part of a Series in which 
        # the images are temporally related. This sounds like the case for orthodontic
        # intraoral and extraoral photograph sets.
        self.ds.ContentDate = date_captured.strftime(defaults.DATE_FORMAT)

    def set_time_captured(self,time_captured):
        self.ds.ContentTime = time_captured.strftime(defaults.TIME_FORMAT)  # long format with micro seconds

    def save_implicit_little_endian(self,filename):
        # Set the transfer syntax
        self.ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        self.ds.is_little_endian = True
        self.ds.is_implicit_VR = True

        logging.debug("Writing test file as Little Endian Implicit VR [{}]".format(filename))
        self.ds.save_as(filename,write_like_original=False)
        logging.info("File [{}] saved.".format(filename))

    def save_explicit_big_endian(self,filename):
        # Write as a different transfer syntax XXX shouldn't need this but pydicom
        # 0.9.5 bug not recognizing transfer syntax
        self.ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
        self.ds.is_little_endian = False
        self.ds.is_implicit_VR = False

        logging.debug("Writing test file as Big Endian Explicit VR [{}]".format(filename))
        self.ds.save_as(filename, write_like_original=False)
        logging.info("File [{}] saved.".format(filename))

    def load(self,filename):
        self.ds = pydicom.dcmread(filename)

    def print(self):
        print(self.ds)


class PhotographBase(DicomBase):
    """
    A.32.4 VL Photographic Image IOD 
    """

    def __init__(self):
        super().__init__()
        self.set_file_meta()


    def set_dataset(self,filename=None):
        super().set_dataset(filename)
        self.ds.Modality = 'XC'

    def set_image_type(self):
        """
        Define if this is a scanned image, or an original capture.
        C.8.12.1.1.6 Image Type
            The Image Type Attribute identifies important image characteristics in a multiple valued Data Element. For Visible Light, Image Type is specialized as follows:

            Value 1 shall identify the Pixel Data Characteristics in accordance with Section C.7.6.1.1.2.

                Enumerated Values:

                ORIGINAL

                DERIVED

            Value 2 shall identify the Patient Examination Characteristics in accordance with Section C.7.6.1.1.2.

                Enumerated Values:

                PRIMARY

                SECONDARY

            Value 3 may be absent, but if present shall identify the members of a stereo pair, in which case Referenced Image Sequence (0008,1140) is used to identify the other member of the pair.

                Enumerated Values:

                STEREO L
                Image is the left image (relative to the observer's left) of a stereo pair acquisition

                STEREO R
                Image is the right image (relative to the observer's right) of a stereo pair acquisition

            Other Values are implementation specific (optional).
        """
        self.ds.ImageType = ['ORIGINAL','PRIMARY']

    def is_digitized_image(self):
        """
        A digitized image is considered as secondary capture for DICOM. As an example, if the original photograph was taken with an analog camera, and the negative, positive or print was then scanned, the scanned image should be recorded in DICOM as secondary, and this method should be used.
        See C.7.6.1.1.2 Image Type
        """
        self.ds.ImageType[1] = 'SECONDARY'

    def is_primary_image(self):
        """
        A primary image is one that was generated by the device that was used to capture the original photograph from the patient. As an example, if the original photograph was taken with a digital camera, that image should be recorded in DICOM using this method.
        See C.7.6.1.1.2 Image Type
        """
        self.ds.ImageType[1] = 'PRIMARY'

    def is_original_image(self):
        self.ds.ImageType[0] = 'ORIGINAL'

    def is_derived_image(self):
        """
        A derived image is a manipulated image. It's not the original anymore, it's been most likely enhanced with some calculation or filters.
        """
        self.ds.ImageType[0] = 'DERIVED'

    def set_image(self,filename=None):
        if not hasattr(self.ds, 'input_image_filename'):
            self.ds.input_image_filename = filename

        with PIL.Image.open(self.ds.input_image_filename) as im:

            # Note

            self.ds.Rows = im.size[1]
            self.ds.Columns = im.size[0]

            if im.mode == '1': # (1-bit pixels, black and white, stored with one pixel per byte)
                self.ds.SamplesPerPixel = 1
                try:
                    del self.ds.PlanarConfiguration
                except AttributeError:
                    pass
                self.ds.BitsStored = 1
                self.ds.HighBit = 0
                self.ds.PhotometricInterpretation = 'MONOCHROME2'
            elif im.mode == 'L': # (8-bit pixels, black and white)
                self.ds.SamplesPerPixel = 1
                try:
                    del self.ds.PlanarConfiguration
                except AttributeError:
                    pass
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'MONOCHROME2'
            elif im.mode == 'P': # (8-bit pixels, mapped to any other mode using a color palette)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError

                # self.ds.SamplesPerPixel = 1
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'PALETTE COLOR'
            elif im.mode == 'RGB': # (3x8-bit pixels, true color)
                self.ds.SamplesPerPixel = 3
                # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'RGB'
            elif im.mode == 'RGBA': # (4x8-bit pixels, true color with transparency mask)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 4
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'ARGB'
            elif im.mode == 'CMYK': #  (4x8-bit pixels, color separation)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 4
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'CMYK'
            elif im.mode == 'YCbCr': # (3x8-bit pixels, color video format) Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 3
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'YBR_FULL'
            elif im.mode == 'LAB': # (3x8-bit pixels, the L*a*b color space)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            elif im.mode == 'HSV': # (3x8-bit pixels, Hue, Saturation, Value color space)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            elif im.mode == 'I': # (32-bit signed integer pixels)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            elif im.mode == 'F': # (32-bit floating point pixels)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError

            px = im.load()
            self.ds.PixelRepresentation = 0x0
            # Image Pixel M
            # Pixel Data (7FE0,0010) for this image. The order of pixels encoded for each image plane is left to right, top to bottom, i.e., the upper left pixel (labeled 1,1) is encoded first followed by the remainder of row 1, followed by the first pixel of row 2 (labeled 2,1) then the remainder of row 2 and so on.
            # It's Planar Configuration which defines how the values are stored in the PixelData, which is defined to be 0, in this case.
            # C.7.6.3.1.3 Planar Configuration
            # Planar Configuration (0028,0006) indicates whether the color pixel data are encoded color-by-plane or color-by-pixel. This Attribute shall be present if Samples per Pixel (0028,0002) has a value greater than 1. It shall not be present otherwise.

            # Enumerated Values:

            # 0
            # The sample values for the first pixel are followed by the sample values for the second pixel, etc. For RGB images, this means the order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, …, etc.
            self.ds.PixelData = b''
            if self.ds.SamplesPerPixel == 1:
                for row in range(self.ds.Rows):
                    for column in range(self.ds.Columns):
                        self.ds.PixelData += bytes([px[column,row]])
            elif self.ds.SamplesPerPixel > 1:
                for row in range(self.ds.Rows):
                    for column in range(self.ds.Columns):
                        for sample in range(self.ds.SamplesPerPixel):
                            self.ds.PixelData += bytes([px[column,row][sample]])
            else:
                print("Error: Incorrect value for SamplesPerPixel {}".format(self.ds.SamplesPerPixel))

            # PixelData has to always be divisible by 2. Add an extra byte if it's not.
            if len(self.ds.PixelData) % 2 == 1:
                self.ds.PixelData += b'0'
