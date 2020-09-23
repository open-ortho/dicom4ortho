from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

import dicom_photo.m_dental_acquisition_context_module

class OrthodonticPhotographTypes(object):
    ''' Orthodontic Photograph Types as defined in ADA WP-1100

    Naming convention: types are prefixes wit an underscore to indicate that
    these are private types, with the additional benefit that the term 45 can
    follow the same convention. Python does not allow variable or funcion
    names to start with a digit.
    '''
    def __init__(self,tooth_number=None):
        self.EV01 = [self._EO,self._RP,self._LR,self._CO]
        self.EV02 = [self._EO,self._RP,self._LR,self._CR]
        self.EV03 = [self._EO,self._RP,self._LC,self._CO]
        self.EV04 = [self._EO,self._RP,self._LC,self._CR]
        self.EV05 = [self._EO,self._RP,self._FS,self._CO]
        self.EV06 = [self._EO,self._RP,self._FS,self._CR]
        self.EV07 = [self._EO,self._RP,self._PF,self._or_none]
        self.EV08 = [self._EO,self._RP,self._LR,self._CO,self._45]
        self.EV09 = [self._EO,self._RP,self._LR,self._CR,self._45]
        self.EV10 = [self._EO,self._LP,self._LC,self._CO,self._45]
        self.EV11 = [self._EO,self._RP,self._LC,self._CR,self._45]
        self.EV12 = [self._EO,self._RP,self._FS,self._CO,self._45]
        self.EV13 = [self._EO,self._RP,self._FS,self._CR,self._45]
        self.EV14 = [self._EO,self._RP,self._PF,self._45]
        self.EV15 = [self._EO,self._FF,self._LR,self._CO]
        self.EV16 = [self._EO,self._FF,self._LR,self._CR]
        self.EV17 = [self._EO,self._FF,self._LC,self._CO]
        self.EV18 = [self._EO,self._FF,self._LC,self._CR]
        self.EV19 = [self._EO,self._FF,self._FS,self._CO]
        self.EV20 = [self._EO,self._FF,self._FS,self._CR]
        self.EV21 = [self._EO,self._FF,self._PF]
        self.EV22 = [self._EO,self._LP,self._LR,self._CO]
        self.EV23 = [self._EO,self._LP,self._LR,self._CR]
        self.EV24 = [self._EO,self._LP,self._LC,self._CO]
        self.EV25 = [self._EO,self._LC,self._LC,self._CR]
        self.EV26 = [self._EO,self._LP,self._FS,self._CO]
        self.EV27 = [self._EO,self._LP,self._FS,self._CR]
        self.EV28 = [self._EO,self._LP,self._FS]
        self.EV29 = [self._EO,self._LP,self._LR,self._CO,self._45]
        self.EV30 = [self._EO,self._LP,self._LC,self._CR,self._45]
        self.EV31 = [self._EO,self._LP,self._LC,self._CO,self._45]
        self.EV32 = [self._EO,self._LP,self._LC,self._CR,self._45]
        self.EV33 = [self._EO,self._LP,self._FS,self._CO,self._45]
        self.EV34 = [self._EO,self._LP,self._FS,self._CR,self._45]
        self.EV35 = [self._EO,self._LP,self._PF,self._45]
        self.EV36 = [self._EO,self._OF,self._IV]
        self.EV37 = [self._EO,self._OF,self._SV]
        self.EV38 = [self._EO,self._OF,self._CS]
        self.EV39 = [self._EO,self._OF,self._OC]
        self.EV40 = [self._EO,self._OF,self._FI]
        self.EV41 = [self._EO,self._OF,self._AN]
        self.EV42 = [self._EO,self._FF,self._MO]
        self.EV43 = [self._EO,self._FF,self._NW]

        self.IV01 = [self._IO,self._RB,self._CO]
        self.IV02 = [self._IO,self._RB,self._CO,self._WM]
        self.IV03 = [self._IO,self._RB,self._CO,self._WM_BC]
        self.IV04 = [self._IO,self._RB,self._CR,self._NM]
        self.IV05 = [self._IO,self._RB,self._CR,self._WM]
        self.IV06 = [self._IO,self._RB,self._CR,self._WM_BC]
        self.IV07 = [self._IO,self._FV,self._CO,self._NM]
        self.IV08 = [self._IO,self._FV,self._CR,self._NM]
        self.IV09 = [self._IO,self._FV,self._TA,self._NM]
        self.IV10 = [self._IO,self._FV,self._MO,self._NM]
        self.IV11 = [self._IO,self._FV,self._IV,self._CO,self._NM]
        self.IV12 = [self._IO,self._FV,self._IV,self._CR,self._NM]
        self.IV13 = [self._IO,self._FV,self._TT,self._NM]
        self.IV14 = [self._IO,self._RL,self._CR,self._OJ,self._NM]
        self.IV15 = [self._IO,self._RL,self._CO,self._OJ,self._NM]
        self.IV16 = [self._IO,self._LL,self._CO,self._OJ,self._NM]
        self.IV17 = [self._IO,self._LL,self._CR,self._OJ,self._NM]
        self.IV18 = [self._IO,self._LB,self._CO,self._NM]
        self.IV19 = [self._IO,self._LB,self._CO,self._WM]
        self.IV20 = [self._IO,self._LB,self._CO,self._WM_BC]
        self.IV21 = [self._IO,self._LB,self._CR,self._NM]
        self.IV22 = [self._IO,self._LB,self._CR,self._WM]
        self.IV23 = [self._IO,self._LB,self._CR,self._WM_BC]
        self.IV24 = [self._IO,self._MX,self._MO,self._OV,self._WM]
        self.IV25 = [self._IO,self._MX,self._MO,self._OV,self._WM_BC]
        self.IV26 = [self._IO,self._MD,self._MO,self._OV,self._WM]
        self.IV27 = [self._IO,self._MD,self._MO,self._OV,self._WM_BC]
        self.IV28 = [self._IO,self._GR]
        self.IV29 = [self._IO,self._FR]
        self.IV30 = [self._IO,self._PA]


    def _EO(self,dataset):
        pass

    def _IO(self,dataset):
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

    def _NM(self,dataset):
        """ No Mirror
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

    def _validate_tooth_number(self,tooth):
        valid_teeth = [
            '11','12','13','14','15','16','17','18',
            '21','22','23','24','25','26','27','28',
            '31','32','33','34','35','36','37','38',
            '41','42','43','44','45','46','47','48',
            '51','52','53','54','55',
            '61','62','63','64','65',
            '71','72','73','74','75',
            '81','82','83','84','85'
        ]

        if tooth in valid_teeth: return True
        else: return False

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