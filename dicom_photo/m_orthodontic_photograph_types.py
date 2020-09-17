from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

import dicom_photo.m_dental_acquisition_context_module

class OrthodonticPhotographTypes(object):
    EV01 = []
    EV02 = []

    def __init__(self):
        self.EV01 = [self.EO,self.RP,self.LR,self.CO]
        self.EV02 = [self.EO,self.RP,self.LR,self.CR]


    def EO(self,dataset):
        pass

    def RP(self, dataset):
        """ Right Profile
        """
        self._face(dataset)
        dataset.ImageLaterality = 'R'
        dataset.AcquisitionView = self._get_sct_code_sequence('30730003','Sagittal (qualifier value)')
        dataset.PatientOrientation = ['A','F'] # Anterior, Foot

    def LP(self, dataset):
        """ Right Profile
        """
        self._face(dataset)
        dataset.ImageLaterality = 'L'
        dataset.PatientOrientation = ['P','F'] # Anterior, Foot

    def FF(self, dataset):
        self._face(dataset)
        dataset.ImageLaterality = 'B' # Both
        dataset.PatientOrientation = ['R','F'] # Right, Foot

    def LR(self,dataset):
        """ Lips Relaxed
        """
        dataset.FunctionalCondition = self._get_sct_code_sequence('745165', 'Lips relaxed')

    def CO(self,dataset):
        dataset.OcclusalRelationship = self._get_sct_code_sequence('110320000',
            'Centric occlusion (observable entity)')

    def CR(self,dataset):
        dataset.OcclusalRelationship = self._get_sct_code_sequence('736783005',
            'Centric relation (observable entity)')

    def _face(self,dataset):
        a_r_s = self._get_sct_code_sequence('302549007','Entire face (body structure)')
        a_r_s[0].AnatomicRegionModifierSequence = \
                self._get_sct_code_sequence('276727009','Null (qualifier value)')
        dataset.AnatomicRegionSequence = a_r_s

    def _get_sct_code_sequence(self,value,meaning):
        code_dataset = Dataset()
        code_dataset.CodeMeaning = meaning
        code_dataset.CodeValue = value
        code_dataset.CodingSchemeDesignator = 'SCT'
        return Sequence([code_dataset])


"""
    # General Image Module M
    dataset.InstanceNumber = '1'
    dataset.PatientOrientation = ''


    # Laterality (0020,0060) is a Series level Attribute and must be the same for
    # all Images in the Series, hence it must be absent if Image Laterality (0020,0062) 
    # has different values for Images in the same Series.
    # In the case of orthodontic photographic session, we need to identify if we 
    # should store one image per series, and entire set in the same study, 
    # or entire set in the same series.
    dataset.ImageLaterality = ''



    # Note
    # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
    dataset.PlanarConfiguration = 0



    # Acquistion Context M
    dataset.AcquisitionContextSequence = pydicom.sequence.Sequence([])
    dataset.AnatomicRegionSequence = pydicom.sequence.Sequence([])

    # VL Image M
    dataset.LossyImageCompression = '00'

    # SOP Common M
    dataset.SOPClassUID = SOPClassUID
    dataset.SOPInstanceUID = SOPInstanceUID

def dciodvfy(filename):
    print('\nValidating file {}'.format(filename))
    dicom3tools_path = '/Users/cdatasettaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'
    os.system('{} {}'.format(
        os.path.join(dicom3tools_path,'dciodvfy'),
        filename))




# reopen the data just for checking
# for filename in (filename_little_endian):
print('Load file {} ...'.format(filename))
dataset = pydicom.dcmread(filename)
print(dataset)
dciodvfy(filename)

# remove the created file
print('Remove file {} ...'.format(filename))
os.remove(filename)
"""