"""
The model.
"""
import datetime
import logging

import pydicom
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset, FileDataset
from pynetdicom.sop_class import VLPhotographicImageStorage
import PIL

import dicom_photo.defaults as defaults
import dicom_photo.m_orthodontic_photograph_types

class DicomBase(object):
    """ Functions and fields common to most DICOM images.
    """

    def __init__(self,**kwargs):
        self.sop_instance_uid = defaults.generate_dicom_uid()
        self.time_string = datetime.datetime.now().strftime(defaults.TIME_FORMAT)
        self.date_string = datetime.datetime.now().strftime(defaults.DATE_FORMAT)
        self.input_image_filename = kwargs['input_image_filename']
        self.output_image_filename = kwargs['output_image_filename']
        self.file_meta = Dataset()
        self._ds = None
        self._set_dataset()
        self._set_general_series()
        self._set_general_study()
        self._set_general_image()
        self._set_acquisition_context()
        self._set_sop_common()

    def set_file_meta(self):
        self.file_meta.MediaStorageSOPInstanceUID = self.sop_instance_uid
        self.file_meta.ImplementationClassUID = defaults.IMPLEMENTATION_CLASS_UID

    def _set_dataset(self):
        self._ds = FileDataset(
            self.output_image_filename,
            {},
            file_meta=self.file_meta, 
            preamble=defaults.DICOM_PREAMBLE)

        self._ds.PatientName = "^"

    def _set_general_study(self):
        self._ds.AccessionNumber = ''
        self._ds.StudyInstanceUID = defaults.generate_dicom_uid()
        self._ds.StudyID = defaults.IDS_NUMBERS
        self._ds.StudyDate = self.date_string
        self._ds.StudyTime = self.time_string

    def _set_general_series(self):
        self._ds.SeriesInstanceUID = defaults.generate_dicom_uid()
        self._ds.SeriesNumber = defaults.IDS_NUMBERS

    def _set_general_image(self):
        self._ds.InstanceNumber = defaults.IDS_NUMBERS
        self._ds_PatientOrientation = ''

    def _set_acquisition_context(self):
        self._ds.AcquisitionContextSequence = Sequence([])

    def _set_sop_common(self):
        self._ds.SOPInstanceUID = self.sop_instance_uid


    @property
    def patient_firstname(self):
        return self._ds.PatientName.split('^')[0]

    @patient_firstname.setter
    def patient_firstname(self, firstname):
        self._ds.PatientName = "{}^{}".format(
            firstname,
            str(self._ds.PatientName).split('^')[1])

    @property
    def patient_lastname(self):
        return self._ds.PatientName.split('^')[1]

    @patient_lastname.setter
    def patient_lastname(self, lastname):
        self._ds.PatientName = "{}^{}".format(
            lastname,
            str(self._ds.PatientName).split('^')[0])

    @property
    def patient_id(self):
        return self._ds.PatientID

    @patient_id.setter
    def patient_id(self, patient_id):
        self._ds.PatientID = patient_id

    @property
    def patient_sex(self):
        return self._ds.PatientSex

    @patient_sex.setter
    def patient_sex(self, patient_sex):
        self._ds.PatientSex = patient_sex

    @property
    def patient_birthdate(self):
        return datetime.datetime.strptime(self._ds.PatientBirthDate, defaults.DATE_FORMAT).date()

    @patient_birthdate.setter
    def patient_birthdate(self, patient_birthdate):
        self._ds.PatientBirthDate = patient_birthdate.strftime(defaults.DATE_FORMAT)

    @property
    def dental_provider_firstname(self):
        return self._ds.ReferringPhysicianName.split('^')[0]

    @dental_provider_firstname.setter
    def dental_provider_firstname(self,firstname):
        if not hasattr(self._ds, 'ReferringPhysicianName'):
            self._ds.ReferringPhysicianName = "^"

        self._ds.ReferringPhysicianName = "{}^{}".format(
            firstname,
            str(self._ds.ReferringPhysicianName).split('^')[1])

    @property
    def dental_provider_lastname(self):
        return self._ds.ReferringPhysicianName.split('^')[1]

    @dental_provider_lastname.setter
    def dental_provider_lastname(self,firstname):
        if self._ds.ReferringPhysicianName is None:
            self._ds.ReferringPhysicianName = "^"

        self._ds.ReferringPhysicianName = "{}^{}".format(
            firstname,
            str(self._ds.ReferringPhysicianName).split('^')[0])

    @property
    def date_captured(self):
        ''' Date of image capture.

        Date and time are required if images is part of a Series in which the
        images are temporally related. This sounds like the case for
        orthodontic intraoral and extraoral photograph sets. return
        datetime.datetime.strptime(self.ds.ContentDate,
        defaults.DATE_FORMAT).date()
        '''
        return datetime.datetime.strptime(self._ds.ContentDate, defaults.DATE_FORMAT).date()

    @date_captured.setter
    def date_captured(self,date_captured):
        # Date and time are required if images is part of a Series in which
        # the images are temporally related. This sounds like the case for orthodontic
        # intraoral and extraoral photograph sets.
        self._ds.ContentDate = date_captured.strftime(defaults.DATE_FORMAT)

    @property
    def equipment_manufacturer(self):
        return self._ds.manufacturer

    @equipment_manufacturer.setter
    def equipment_manufacturer(self, manufacturer):
        self._ds.Manufacturer = manufacturer

    def set_time_captured(self,time_captured):
        """
        """
        self._ds.ContentTime = time_captured.strftime(defaults.TIME_FORMAT)  # long format with micro seconds

    def save_implicit_little_endian(self,filename=None):
        if filename is None:
            filename = self.output_image_filename

        # Set the transfer syntax
        self._ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = True

        logging.debug("Writing test file as Little Endian Implicit VR [{}]", filename)
        self._ds.save_as(filename,write_like_original=False)
        logging.info("File [{}] saved.".format(filename))

    def save_explicit_big_endian(self,filename=None):
        if filename is None:
            filename = self.output_image_filename
        # Write as a different transfer syntax XXX shouldn't need this but pydicom
        # 0.9.5 bug not recognizing transfer syntax
        self._ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
        self._ds.is_little_endian = False
        self._ds.is_implicit_VR = False

        logging.debug("Writing test file as Big Endian Explicit VR [{}]", filename)
        self._ds.save_as(filename, write_like_original=False)
        logging.info("File [{}] saved.",filename)

    def load(self,filename):
        self._ds = pydicom.dcmread(filename)

    def print(self):
        print(self._ds)

class PhotographBase(DicomBase):
    """
    A.32.4 VL Photographic Image IOD 
    """

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.set_file_meta()
        self.file_meta.MediaStorageSOPClassUID = VLPhotographicImageStorage
        self._set_sop_common()
        self._set_general_series()
        self._set_vl_image()

    def _set_sop_common(self):
        super()._set_sop_common()
        self._ds.SOPClassUID = VLPhotographicImageStorage
    
    def _set_general_series(self):
        super()._set_general_series()
        self._ds.Modality = 'XC'

    def _set_vl_image(self):
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
        self._ds.ImageType = ['ORIGINAL','PRIMARY']

        # Specifies whether an Image has undergone lossy compression (at a
        # point in its lifetime).
        self._ds.LossyImageCompression = '' 

    def is_digitized_image(self):
        """
        A digitized image is considered as secondary capture for DICOM. As an example, if the original photograph was taken with an analog camera, and the negative, positive or print was then scanned, the scanned image should be recorded in DICOM as secondary, and this method should be used.
        See C.7.6.1.1.2 Image Type
        """
        self._ds.ImageType[1] = 'SECONDARY'

    def is_primary_image(self):
        """ A primary image is one that was generated by the device that was
        used to capture the original photograph from the patient.
        
        As an example, if the original photograph was taken with a digital
        camera, that image should be recorded in DICOM using this method. See
        C.7.6.1.1.2 Image Type
        """
        self._ds.ImageType[1] = 'PRIMARY'

    def is_original_image(self):
        self._ds.ImageType[0] = 'ORIGINAL'

    def is_derived_image(self):
        """ A derived image is a manipulated image. 
        
        It's not the original anymore, it's been most likely enhanced with
        some calculation or filters.
        """
        self._ds.ImageType[0] = 'DERIVED'

    def lossy_compression(self, lossy):
        if lossy == True:
            self._ds.LossyImageCompression('01')
        elif lossy == False:
            self._ds.LossyImageCompression('00')

    def set_image(self,filename=None):
        if filename is not None and not hasattr(self._ds, 'input_image_filename'):
            self._ds.input_image_filename = filename

        with PIL.Image.open(self.input_image_filename) as im:

            # Note

            self._ds.Rows = im.size[1]
            self._ds.Columns = im.size[0]

            if im.mode == '1': # (1-bit pixels, black and white, stored with one pixel per byte)
                self._ds.SamplesPerPixel = 1
                try:
                    del self._ds.PlanarConfiguration
                except AttributeError:
                    pass
                self._ds.BitsStored = 1
                self._ds.HighBit = 0
                self._ds.PhotometricInterpretation = 'MONOCHROME2'
            elif im.mode == 'L': # (8-bit pixels, black and white)
                self._ds.SamplesPerPixel = 1
                try:
                    del self._ds.PlanarConfiguration
                except AttributeError:
                    pass
                self._ds.BitsAllocated = 8
                self._ds.BitsStored = 8
                self._ds.HighBit = 7
                self._ds.PhotometricInterpretation = 'MONOCHROME2'
            elif im.mode == 'P': # (8-bit pixels, mapped to any other mode using a color palette)
                print("ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError

                # self.ds.SamplesPerPixel = 1
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'PALETTE COLOR'
            elif im.mode == 'RGB': # (3x8-bit pixels, true color)
                self._ds.SamplesPerPixel = 3
                # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
                self._ds.PlanarConfiguration = 0
                self._ds.BitsAllocated = 8
                self._ds.BitsStored = 8
                self._ds.HighBit = 7
                self._ds.PhotometricInterpretation = 'RGB'
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
            self._ds.PixelRepresentation = 0x0
            # Image Pixel M
            # Pixel Data (7FE0,0010) for this image. The order of pixels encoded for each image plane is left to right, top to bottom, i.e., the upper left pixel (labeled 1,1) is encoded first followed by the remainder of row 1, followed by the first pixel of row 2 (labeled 2,1) then the remainder of row 2 and so on.
            # It's Planar Configuration which defines how the values are stored in the PixelData, which is defined to be 0, in this case.
            # C.7.6.3.1.3 Planar Configuration
            # Planar Configuration (0028,0006) indicates whether the color pixel data are encoded color-by-plane or color-by-pixel. This Attribute shall be present if Samples per Pixel (0028,0002) has a value greater than 1. It shall not be present otherwise.

            # Enumerated Values:

            # 0
            # The sample values for the first pixel are followed by the sample values for the second pixel, etc. For RGB images, this means the order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, …, etc.
            self._ds.PixelData = b''
            if self._ds.SamplesPerPixel == 1:
                for row in range(self._ds.Rows):
                    for column in range(self._ds.Columns):
                        self._ds.PixelData += bytes([px[column,row]])
            elif self._ds.SamplesPerPixel > 1:
                for row in range(self._ds.Rows):
                    for column in range(self._ds.Columns):
                        for sample in range(self._ds.SamplesPerPixel):
                            self._ds.PixelData += bytes([px[column,row][sample]])
            else:
                print("Error: Incorrect value for SamplesPerPixel {}".format(self._ds.SamplesPerPixel))

            # PixelData has to always be divisible by 2. Add an extra byte if it's not.
            if len(self._ds.PixelData) % 2 == 1:
                self._ds.PixelData += b'0'

class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        arguments:

        photo_type: a 4 digit ortho photo type code as specifed in WP-1100. Ex. EV01

        input_image_filename: name of input image file

        output_image_filename: name of output image file
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if callable(kwargs['photo_type']):
            self._type = kwargs['photo_type']
        else:
            # Allow for both dash separated and not separated naming
            photo_type = kwargs['photo_type'].replace('-','')

            # Get the array of functions to set this required type.
            self._type = (dicom_photo.m_orthodontic_photograph_types.OrthodonticPhotographTypes().views[photo_type])
        
        self._set_dicom_attributes()

    def _set_dicom_attributes(self):
        for set_attr in self._type:
            logging.debug('Setting DICOM attributes for {}', self._type)
            set_attr(self._ds)