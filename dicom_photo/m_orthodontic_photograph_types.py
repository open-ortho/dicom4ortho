from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

import dicom_photo.m_dental_acquisition_context_module

class OrthodonticPhotographTypes(object):
    def __init__(self):
        self.EV01 = [self._EO,self._RP,self._LR,self._CO]
        self.EV02 = [self._EO,self._RP,self._LR,self._CR]
        self.EV03 = [self._EO,self._RP,self._LC,self._CO]
        self.EV04 = [self._EO,self._RP,self._LC,self._CR]
        self.EV05 = [self._EO,self._RP,self._FS,self._CO]
        self.EV06 = [self._EO,self._RP,self._FS,self._CR]
        self.EV07 = [self._EO,self._RP,self._PF,self._or_none]
        self.EV08 = [self._EO,self._RP,self._LR,self._CO,self._45]
        self.EV09 = [self._EO,self._LP,self._LC,self._CO,self._45]
        self.EV10 = [self._EO,self._RP,self._LC,self._CR,self._45]


    def _EO(self,dataset):
        pass

    def _RP(self, dataset):
        """ Right Profile
        """
        self._face(dataset)
        dataset.ImageLaterality = 'R'
        dataset.AcquisitionView = self._get_sct_code_sequence('30730003','Sagittal (qualifier value)')
        dataset.PatientOrientation = ['A','F'] # Anterior, Foot

    def _LP(self, dataset):
        """ Left Profile
        """
        self._face(dataset)
        dataset.ImageLaterality = 'L'
        dataset.PatientOrientation = ['P','F'] # Anterior, Foot

    def _FF(self, dataset):
        self._face(dataset)
        dataset.ImageLaterality = 'B' # Both
        dataset.PatientOrientation = ['R','F'] # Right, Foot

    def _FS(self, dataset):
        """ Full Smile
        """
        self._face(dataset)
        dataset.ImageLaterality = 'B' # Both

    def _LC(self,dataset):
        """ Lips Closed
        """
        dataset.FunctionalCondition = self._get_sct_code_sequence('787607005', 'Lips closed')

    def _LR(self,dataset):
        """ Lips Relaxed
        """
        dataset.FunctionalCondition = self._get_sct_code_sequence('745165', 'Lips relaxed')

    def _CO(self,dataset):
        dataset.OcclusalRelationship = self._get_sct_code_sequence('110320000',
            'Centric occlusion (observable entity)')

    def _CR(self,dataset):
        dataset.OcclusalRelationship = self._get_sct_code_sequence('736783005',
            'Centric relation (observable entity)')
    
    def _or_none(self,dataset):
        """ Null Occlusal Relationship
        """
        dataset.OcclusalRelationship = self._null()

    def _MD(self,dataset):
        """ Mandibular 
        """
        a_r_s = self._get_sct_code_sequence('181812008','Entire mandible (body structure)')
        a_r_s[0].AnatomicRegionModifierSequence = self._null()
        dataset.AnatomicRegionSequence = a_r_s

    def _MX(self,dataset):
        """ Maxillary
        """
        pass

    def _MO(self,dataset):
        """ Mouth Open
        """
        pass

    def _TA(self,dataset):
        """ Teeth Apart
        """
        pass

    def _OJ(self,dataset):
        """ Showing Overjet
        """
        pass

    def _PF(self,dataset):
        """ Mandible Postured Forward
        """
        dataset.FunctionalCondition = self._get_sct_code_sequence('787611004',
            'Photographic image extraoral with mandible postured forward (record artifact)')

    def _OF(self,dataset):
        """ Other Face

        some other view of the face; e.g., with the face tipped back, or from
        above
        """
        pass

    def _WM(self,dataset):
        """ With Mirror

        used for intraoral photographs only. Does not apply to extraoral
        photographs
        """
        pass

    def _WM_BC(self,dataset):
        """ With Mirror But Corrected

        flipped and/or rotated to appear as if it has been taken directly
        without a mirror used for intraoral photographs only. Does not apply
        to extraoral photographs
        """
        pass

    def _RB(self,dataset):
        """ Right Buccal

        used to document posterior occlusion
        """
        pass

    def _LB(self,dataset):
        """ Left Buccal

        used to document posterior occlusion
        """
        pass

    def _RL(self,dataset):
        """ Right Lateral

        used to document the dental occlusion from the subject's right side
        """
        pass

    def _LL(self,dataset):
        """ Left Buccal

        used to document the dental occlusion from the subject's left side
        """
        pass

    def _FV(self,dataset):
        """ Frontal View
        """
        pass

    def _IV(self,dataset):
        """ Inferior View

        use IO.IV to show depth of bite and overjet from below
        """
        pass

    def _SV(self,dataset):
        """ Superior View
        """
        pass

    def _45(self,dataset):
        """ 45º View
        """
        dataset.AcquisitionView = self._get_sct_code_sequence('30730003',
            'Photographic image extraoral with 45 degree view (record artifact)')

    def _OV(self,dataset):
        """ Occlusal View
        """
        pass

    def _CS(self,dataset):
        """ Close-up Smile
        """
        pass

    def _OC(self,dataset):
        """ Occlusal Cant
        """
        pass

    def _FI(self,dataset):
        """ Forensic Interest
        """
        pass

    def _NW(self,dataset):
        """ Nerve Weakness
        """
        pass

    def _AN(self,dataset):
        """ Anomalies
        """
        pass

    def _FR(self,dataset):
        """ Frenum
        """
        pass

    def _PA(self,dataset):
        """ Using Photo Accessory

        such as a photo contraster providing a solid background or black
        mirror. Can be appended to any intraoral (IO) view code as needed
        """
        pass

    def _TT(self,dataset):
        """ Tongue Thrust
        """
        pass 

    def _IN(self,dataset):
        """ Initial

        refers to Initial time point, generally observation or pre-treatment
        """
        pass

    def _P(self,dataset):
        """ Progress

        refers to Progress time point, i.e. progress photos
        """
        pass

    def _F(self,dataset):
        """ Final

        refers to Final time point, generally when treatment is finished
        """
        pass
    def _FU(self,dataset):
        """ Follow-Up

        refers to Follow-Up time point, generally taken to show
        post-treatment changes
        """
        pass

    def _null(self):
        return self._get_sct_code_sequence('276727009','Null (qualifier value)')

    def _mandible(self,dataset):
        a_r_s = self._get_sct_code_sequence('181812008','Entire mandible (body structure)')
        a_r_s[0].AnatomicRegionModifierSequence = self._null()
        dataset.AnatomicRegionSequence = a_r_s

    def _face(self,dataset):
        a_r_s = self._get_sct_code_sequence('302549007','Entire face (body structure)')
        a_r_s[0].AnatomicRegionModifierSequence = self._null()
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