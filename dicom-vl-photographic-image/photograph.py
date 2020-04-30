"""
A.32.4 VL Photographic Image IOD

"""
import os
import tempfile
import datetime
import defaults

import pydicom
from pydicom.dataset import Dataset, FileDataset
import pydicom.sequence
import PIL

class DentalPhotograph:

    def __init__(self):
        self.SOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.4'
        self.SOPInstanceUID = "1.2.3"
        self.timeStr = datetime.datetime.now().strftime('%H%M%S.%f')  # long format with micro seconds
        self.dateStr = datetime.datetime.now().strftime('%Y%m%d')
        # self.preamble = None
        self.preamble = b"\0" * 128


        # Create some temporary filenames
        suffix = '.dcm'
        filename_little_endian = tempfile.NamedTemporaryFile(suffix=suffix).name
        filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name

        print("Setting file meta information...")
        # Populate required values for file meta information
        file_meta = Dataset()

        file_meta.MediaStorageSOPClassUID = SOPClassUID
        file_meta.MediaStorageSOPInstanceUID = SOPInstanceUID
        file_meta.ImplementationClassUID = "1.2.3.4"
        # file_meta.FileMetaInformationGroupLength = 2
        # file_meta.FileMetaInformationVersion = b'01'

    def set_defaults(self):
        print("Setting dataset values...")
        # Create the FileDataset instance (initially no data elements, but file_meta
        # supplied)
        self.ds = FileDataset(filename_little_endian, {},
                        file_meta=file_meta, preamble=preamble)

        self.ds.Modality = 'XC'
        self.ds.PatientName = "^"
        self.ds.StudyDate = dateStr
        self.ds.StudyTime = timeStr

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
        self.ds.PatientBirthDate = patient_birthdate.strftime(defaults.date_format)

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
        self.ds.ContentDate = date_captured.strftime(defaults.date_format)

    def set_time_captured(self,time_captured):
        self.ds.ContentTime = time_captured.strftime(defaults.time_format)  # long format with micro seconds

    def set_image(self,image_path):
        with PIL.Image.open(image_path) as im:

            # Note

            self.ds.Rows = im.size[1]
            self.ds.Columns = im.size[0]

            if im.mode == '1': # (1-bit pixels, black and white, stored with one pixel per byte)
                self.ds.SamplesPerPixel = 1
                self.ds.BitsAllocated = 1
                self.ds.BitsStored = 1
                self.ds.HighBit = 0
                self.ds.PhotometricInterpretation = 'MONOCHROME1'
            elif im.mode == 'L': # (8-bit pixels, black and white)
                self.ds.SamplesPerPixel = 1
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'MONOCHROME1'
            elif im.mode == 'P': # (8-bit pixels, mapped to any other mode using a color palette)
                self.ds.SamplesPerPixel = 1
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'PALETTE COLOR'
            elif im.mode == 'RGB': # (3x8-bit pixels, true color)
                self.ds.SamplesPerPixel = 3
                # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'RGB'
            elif im.mode == 'RGBA': # (4x8-bit pixels, true color with transparency mask)
                self.ds.SamplesPerPixel = 4
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'ARGB'
            elif im.mode == 'CMYK': #  (4x8-bit pixels, color separation)
                self.ds.SamplesPerPixel = 4
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'CMYK'
            elif im.mode == 'YCbCr': # (3x8-bit pixels, color video format) Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
                self.ds.SamplesPerPixel = 3
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
                self.ds.PhotometricInterpretation = 'YBR_FULL'
            elif im.mode == 'LAB': # (3x8-bit pixels, the L*a*b color space)
                self.ds.SamplesPerPixel = 3
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
            elif im.mode == 'HSV': # (3x8-bit pixels, Hue, Saturation, Value color space)
                self.ds.SamplesPerPixel = 3
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 8
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
            elif im.mode == 'I': # (32-bit signed integer pixels)
                self.ds.SamplesPerPixel = 3
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 32
                self.ds.BitsStored = 8
                self.ds.HighBit = 7
            elif im.mode == 'F': # (32-bit floating point pixels)
                self.ds.SamplesPerPixel = 3
                self.ds.PlanarConfiguration = 0
                self.ds.BitsAllocated = 32
                self.ds.BitsStored = 8
                self.ds.HighBit = 7

            px = im.load()
            self.ds.PixelRepresentation = 0x0
            # Image Pixel M
            # Pixel Data (7FE0,0010) for this image. The order of pixels encoded for each image plane is left to right, top to bottom, i.e., the upper left pixel (labeled 1,1) is encoded first followed by the remainder of row 1, followed by the first pixel of row 2 (labeled 2,1) then the remainder of row 2 and so on.
            self.ds.PixelData = b''
            if ds.SamplesPerPixel == 1:
                for row in range(self.ds.Rows):
                    for column in range(self.ds.Columns):
                        self.ds.PixelData += px[row,column]
            elif ds.SamplesPerPixel > 1:
                for row in range(self.ds.Rows):
                    for column in range(self.ds.Columns):
                        for sample in range(self.ds.SamplesPerPixel):
                            self.ds.PixelData += px[row,column][sample]
            else:
                print("Error: Incorrect value for SamplesPerPixel {}".format(ds.SamplesPerPixel))

    # General Study Module M
    ds.StudyInstanceUID = '1'
    ds.StudyID = '1'
    ds.AccessionNumber = '1'

    # General Series Module M
    ds.SeriesInstanceUID = '1'
    ds.SeriesNumber = '1'
    # ds.Laterality = ''

    # General Equipment Module M
    ds.Manufacturer = ''

    # VL Photographic Equipment Module U
    # ds.CameraOwnerName = ''
    # ds.LensSepcification = ''
    # ds.LensMake = ''
    # ds.LensModel = ''
    # ds.LensSerialNumber = ''


    # General Image Module M
    ds.InstanceNumber = '1'
    ds.PatientOrientation = ''


    # Laterality (0020,0060) is a Series level Attribute and must be the same for
    # all Images in the Series, hence it must be absent if Image Laterality (0020,0062) 
    # has different values for Images in the same Series.
    # In the case of orthodontic photographic session, we need to identify if we 
    # should store one image per series, and entire set in the same study, 
    # or entire set in the same series.
    ds.ImageLaterality = ''


    # C.7.6.3.1.3 Planar Configuration
    # Planar Configuration (0028,0006) indicates whether the color pixel data are encoded color-by-plane or color-by-pixel. This Attribute shall be present if Samples per Pixel (0028,0002) has a value greater than 1. It shall not be present otherwise.

    # Enumerated Values:

    # 0
    # The sample values for the first pixel are followed by the sample values for the second pixel, etc. For RGB images, this means the order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, …, etc.

    # 1
    # Each color plane shall be encoded contiguously. For RGB images, this means the order of the pixel values encoded is R1, R2, R3, …, G1, G2, G3, …, B1, B2, B3, etc.

    # Note
    # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
    ds.PlanarConfiguration = 0



    # Acquistion Context M
    ds.AcquisitionContextSequence = pydicom.sequence.Sequence([])
    ds.AnatomicRegionSequence = pydicom.sequence.Sequence([])

    # VL Image M
    ds.LossyImageCompression = '00'
    ds.ImageType = ['ORIGINAL','PRIMARY']
    ds.PhotometricInterpretation = 'RGB'

    # SOP Common M
    ds.SOPClassUID = SOPClassUID
    ds.SOPInstanceUID = SOPInstanceUID

def dciodvfy(filename):
    print('\nValidating file {}'.format(filename))
    dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
    os.system('{} {}'.format(
        os.path.join(dicom3tools_path,'dciodvfy'),
        filename))


# Set the transfer syntax
ds.is_little_endian = True
ds.is_implicit_VR = True

print("Writing test file", filename_little_endian)
ds.save_as(filename_little_endian,write_like_original=False)
print("File saved.")

# Write as a different transfer syntax XXX shouldn't need this but pydicom
# 0.9.5 bug not recognizing transfer syntax
ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
ds.is_little_endian = False
ds.is_implicit_VR = False

print("Writing test file as Big Endian Explicit VR", filename_big_endian)
ds.save_as(filename_big_endian, write_like_original=False)

# reopen the data just for checking
# for filename in (filename_little_endian):
filename = filename_big_endian
print('Load file {} ...'.format(filename))
ds = pydicom.dcmread(filename)
print(ds)
dciodvfy(filename)

# remove the created file
print('Remove file {} ...'.format(filename))
os.remove(filename)