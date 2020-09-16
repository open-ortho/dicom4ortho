from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

import dicom_photo.m_dental_acquisition_context_module

class OrthodonticPhotographTypes(object):
    EV01 = []
    EV02 = []

    def __init__(self):
        self.EV01 = [self.EO,self.RP,self.LR,self.CO]
        self.EV02 = [self.EO,self.RP,self.LR,self.CR]


    def EO(self,ds):
        pass

    def RP(self, ds):
        self._face(ds)
        ds.ImageLaterality = 'R'
        ds.AcquisitionView = self._get_sct_code_sequence('30730003','Sagittal (qualifier value)')

    def LP(self, ds):
        self._face(ds)
        ds.ImageLaterality = 'L'

    def FF(self, ds):
        self._face(ds)
        ds.ImageLaterality = 'B' # Both

    def LR(self,ds):
        ds.FunctionalCondition = self._get_sct_code_sequence('745165', 'Lips relaxed')

    def CO(self,ds):
        ds.OcclusalRelationship = self._get_sct_code_sequence('110320000',
            'Centric occlusion (observable entity)')

    def CR(self,ds):
        ds.OcclusalRelationship = self._get_sct_code_sequence('736783005',
            'Centric relation (observable entity)')

    def _face(self,ds):
        a_r_s = self._get_sct_code_sequence('302549007','Entire face (body structure)')
        a_r_s[0].AnatomicRegionModifierSequence = \
                self._get_sct_code_sequence('276727009','Null (qualifier value)')
        ds.AnatomicRegionSequence = a_r_s

    def _get_sct_code_sequence(self,value,meaning):
        code_ds = Dataset()
        code_ds.CodeMeaning = meaning
        code_ds.CodeValue = value
        code_ds.CodingSchemeDesignator = 'SCT'
        return Sequence([code_ds])


"""
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



    # Note
    # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
    ds.PlanarConfiguration = 0



    # Acquistion Context M
    ds.AcquisitionContextSequence = pydicom.sequence.Sequence([])
    ds.AnatomicRegionSequence = pydicom.sequence.Sequence([])

    # VL Image M
    ds.LossyImageCompression = '00'

    # SOP Common M
    ds.SOPClassUID = SOPClassUID
    ds.SOPInstanceUID = SOPInstanceUID

def dciodvfy(filename):
    print('\nValidating file {}'.format(filename))
    dicom3tools_path = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
    os.system('{} {}'.format(
        os.path.join(dicom3tools_path,'dciodvfy'),
        filename))




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