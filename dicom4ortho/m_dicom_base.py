"""
    # General Study Module M
    ds.StudyInstanceUID = defaults.generate_dicom_uid()
    ds.StudyID = '1'
    ds.AccessionNumber = '1'

    # General Series Module M
    ds.SeriesInstanceUID = defaults.generate_dicom_uid()
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

    # SOP Common M
    ds.SOPClassUID = self.SOPClassUID
    ds.SOPInstanceUID = SOPInstanceUID

def dciodvfy(filename):
    print('\nValidating file {}'.format(filename))
    dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
    os.system('{} {}'.format(
        os.path.join(dicom3tools_path,'dciodvfy'),
        filename))


dp = DentalPhotograph()
dp.set_file_meta()
dp.set_dataset('file1.dcm')
dp.set_patient_firstname('First Name')
dp.set_patient_lastname('Last Name')


# reopen the data just for checking
# for filename in (filename_little_endian):
print('Load file {} ...'.format(filename))
ds = pydicom.dcmread(filename)
print(ds)
dciodvfy(filename)

# remove the created file
print('Remove file {} ...'.format(filename))
os.remove(filename)
"""
