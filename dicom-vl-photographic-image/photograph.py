"""
A.32.4 VL Photographic Image IOD

"""
import os
import tempfile
import datetime

import pydicom
from pydicom.dataset import Dataset, FileDataset


# Create some temporary filenames
suffix = '.dcm'
filename_little_endian = tempfile.NamedTemporaryFile(suffix=suffix).name
filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name

print("Setting file meta information...")
# Populate required values for file meta information
file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
file_meta.MediaStorageSOPInstanceUID = "1.2.3"
file_meta.ImplementationClassUID = "1.2.3.4"

print("Setting dataset values...")
# Create the FileDataset instance (initially no data elements, but file_meta
# supplied)
ds = FileDataset(filename_little_endian, {},
                 file_meta=file_meta, preamble=b"\0" * 128)

# Add the data elements -- not trying to set all required here. Check DICOM
# standard

# Patient Module M
ds.PatientName = "Test^Firstname"
ds.PatientID = "123456"
ds.Patient​Birth​Date = ""
ds.PatientSex = ''

# General Study Module M
ds.StudyInstanceUID = ''
ds.StudyDate = ''
ds.StudyTime = ''
ds.Referring​Physician​Name = ''
ds.StudyID = ''
ds.Accession​Number = ''

# General Series Module M
ds.Modality = 'XC'
ds.Series​Instance​UID = ''
ds.SeriesNumber = ''
ds.Laterality = ''

# General Equipment Module M
ds.Manufacturer = ''

# VL Photographic Equipment Module U
ds.Camera​Owner​Name = ''
ds.LensSepcification = ''
ds.LensMake = ''
ds.LensModel = ''
ds.LensSerialNumber = ''


# General Image Module M
ds.InstanceNumber = ''
ds.PatientOrientation = ''

# Date and time are required if images is part of a Series in which 
# the images are temporally related. This sounds like the case for orthodontic
# intraoral and extraoral photograph sets.
ds.ContentDate = ''
ds.ContentTime = ''

# Laterality (0020,0060) is a Series level Attribute and must be the same for
# all Images in the Series, hence it must be absent if Image Laterality (0020,0062) 
# has different values for Images in the same Series.
# In the case of orthodontic photographic session, we need to identify if we 
# should store one image per series, and entire set in the same study, 
# or entire set in the same series.
ds.ImageLaterality = ''

# Image Pixel M
# Acquistion Context M
# VL Image M
# SOP Common M



# Set the transfer syntax
ds.is_little_endian = True
ds.is_implicit_VR = True

# Set creation date/time
dt = datetime.datetime.now()
ds.ContentDate = dt.strftime('%Y%m%d')
timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
ds.ContentTime = timeStr

print("Writing test file", filename_little_endian)
ds.save_as(filename_little_endian)
print("File saved.")

# Write as a different transfer syntax XXX shouldn't need this but pydicom
# 0.9.5 bug not recognizing transfer syntax
ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
ds.is_little_endian = False
ds.is_implicit_VR = False

print("Writing test file as Big Endian Explicit VR", filename_big_endian)
ds.save_as(filename_big_endian)

# reopen the data just for checking
for filename in (filename_little_endian, filename_big_endian):
    print('Load file {} ...'.format(filename))
    ds = pydicom.dcmread(filename)
    print(ds)

    # remove the created file
    print('Remove file {} ...'.format(filename))
    os.remove(filename)