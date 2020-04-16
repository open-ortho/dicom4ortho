"""
A.32.4 VL Photographic Image IOD

"""
import os
import tempfile
import datetime

import pydicom
from pydicom.dataset import Dataset, FileDataset
import pydicom.sequence

SOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.4'
SOPInstanceUID = "1.2.3"
timeStr = datetime.datetime.now().strftime('%H%M%S.%f')  # long format with micro seconds
dateStr = datetime.datetime.now().strftime('%Y%m%d')
# preamble = None
preamble = b"\0" * 128

def dciodvfy(filename):
    print('\nValidating file {}'.format(filename))
    dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
    os.system('{} {}'.format(
        os.path.join(dicom3tools_path,'dciodvfy'),
        filename))

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

print("Setting dataset values...")
# Create the FileDataset instance (initially no data elements, but file_meta
# supplied)
ds = FileDataset(filename_little_endian, {},
                 file_meta=file_meta, preamble=preamble)

# Add the data elements -- not trying to set all required here. Check DICOM
# standard

# Patient Module M
ds.PatientName = "Test^Firstname"
ds.PatientID = "123456"
ds.PatientBirthDate = '20180916'
ds.PatientSex = 'M'

# General Study Module M
ds.StudyInstanceUID = '1'
ds.StudyDate = dateStr
ds.StudyTime = timeStr
ds.ReferringPhysicianName = 'Open-Ortho^'
ds.StudyID = '1'
ds.AccessionNumber = '1'

# General Series Module M
ds.Modality = 'XC'
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

# Date and time are required if images is part of a Series in which 
# the images are temporally related. This sounds like the case for orthodontic
# intraoral and extraoral photograph sets.
ds.ContentDate = dateStr
ds.ContentTime = timeStr

# Laterality (0020,0060) is a Series level Attribute and must be the same for
# all Images in the Series, hence it must be absent if Image Laterality (0020,0062) 
# has different values for Images in the same Series.
# In the case of orthodontic photographic session, we need to identify if we 
# should store one image per series, and entire set in the same study, 
# or entire set in the same series.
ds.ImageLaterality = ''

# Image Pixel M
ds.PixelData = b'0' * 637776
ds.SamplesPerPixel = 3

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

ds.PhotometricInterpretation = ''
ds.Rows = 516
ds.Columns = 412
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0x0


# Acquistion Context M
ds.AcquisitionContextSequence = pydicom.sequence.Sequence([])

# VL Image M
ds.LossyImageCompression = '00'
ds.ImageType = ['ORIGINAL','PRIMARY']
ds.PhotometricInterpretation = 'RGB'

# SOP Common M
ds.SOPClassUID = SOPClassUID
ds.SOPInstanceUID = SOPInstanceUID

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