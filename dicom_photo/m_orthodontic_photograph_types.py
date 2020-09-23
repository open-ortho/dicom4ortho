''' Add SCT codes in DICOM object for Orthodontic Views.

'''

from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

import dicom_photo.m_dental_acquisition_context_module
import dicom_photo.m_tooth_codes as ToothCodes

class OrthodonticPhotographTypes(object):
    ''' Orthodontic Photograph Types as defined in ADA WP-1100

    Naming convention: types are prefixes wit an underscore to indicate that
    these are private types, with the additional benefit that the term 45 can
    follow the same convention. Python does not allow variable or funcion
    names to start with a digit.

    If teeth are present, add them in a list as strings using ISO tooth
    numbering convention. Example:

    opt = OrthodonticPhotographTypes(teeth=['24','25','26','27','28','34','35','36','37','38'])
    '''
    def __init__(self,teeth=None):
        self.views = {
                "EV01" : [self._EO,self._RP,self._LR,self._CO],
                "EV02" : [self._EO,self._RP,self._LR,self._CR],
                "EV03" : [self._EO,self._RP,self._LC,self._CO],
                "EV04" : [self._EO,self._RP,self._LC,self._CR],
                "EV05" : [self._EO,self._RP,self._FS,self._CO],
                "EV06" : [self._EO,self._RP,self._FS,self._CR],
                "EV07" : [self._EO,self._RP,self._PF,self._or_none],
                "EV08" : [self._EO,self._RP,self._LR,self._CO,self._45],
                "EV09" : [self._EO,self._RP,self._LR,self._CR,self._45],
                "EV10" : [self._EO,self._LP,self._LC,self._CO,self._45],
                "EV11" : [self._EO,self._RP,self._LC,self._CR,self._45],
                "EV12" : [self._EO,self._RP,self._FS,self._CO,self._45],
                "EV13" : [self._EO,self._RP,self._FS,self._CR,self._45],
                "EV14" : [self._EO,self._RP,self._PF,self._45],
                "EV15" : [self._EO,self._FF,self._LR,self._CO],
                "EV16" : [self._EO,self._FF,self._LR,self._CR],
                "EV17" : [self._EO,self._FF,self._LC,self._CO],
                "EV18" : [self._EO,self._FF,self._LC,self._CR],
                "EV19" : [self._EO,self._FF,self._FS,self._CO],
                "EV20" : [self._EO,self._FF,self._FS,self._CR],
                "EV21" : [self._EO,self._FF,self._PF],
                "EV22" : [self._EO,self._LP,self._LR,self._CO],
                "EV23" : [self._EO,self._LP,self._LR,self._CR],
                "EV24" : [self._EO,self._LP,self._LC,self._CO],
                "EV25" : [self._EO,self._LC,self._LC,self._CR],
                "EV26" : [self._EO,self._LP,self._FS,self._CO],
                "EV27" : [self._EO,self._LP,self._FS,self._CR],
                "EV28" : [self._EO,self._LP,self._FS],
                "EV29" : [self._EO,self._LP,self._LR,self._CO,self._45],
                "EV30" : [self._EO,self._LP,self._LC,self._CR,self._45],
                "EV31" : [self._EO,self._LP,self._LC,self._CO,self._45],
                "EV32" : [self._EO,self._LP,self._LC,self._CR,self._45],
                "EV33" : [self._EO,self._LP,self._FS,self._CO,self._45],
                "EV34" : [self._EO,self._LP,self._FS,self._CR,self._45],
                "EV35" : [self._EO,self._LP,self._PF,self._45],
                "EV36" : [self._EO,self._OF,self._IV],
                "EV37" : [self._EO,self._OF,self._SV],
                "EV38" : [self._EO,self._OF,self._CS],
                "EV39" : [self._EO,self._OF,self._OC],
                "EV40" : [self._EO,self._OF,self._FI],
                "EV41" : [self._EO,self._OF,self._AN],
                "EV42" : [self._EO,self._FF,self._MO],
                "EV43" : [self._EO,self._FF,self._NW],

                "IV01" : [self._IO,self._RB,self._CO],
                "IV02" : [self._IO,self._RB,self._CO,self._WM],
                "IV03" : [self._IO,self._RB,self._CO,self._WM_BC],
                "IV04" : [self._IO,self._RB,self._CR,self._NM],
                "IV05" : [self._IO,self._RB,self._CR,self._WM],
                "IV06" : [self._IO,self._RB,self._CR,self._WM_BC],
                "IV07" : [self._IO,self._FV,self._CO,self._NM],
                "IV08" : [self._IO,self._FV,self._CR,self._NM],
                "IV09" : [self._IO,self._FV,self._TA,self._NM],
                "IV10" : [self._IO,self._FV,self._MO,self._NM],
                "IV11" : [self._IO,self._FV,self._IV,self._CO,self._NM],
                "IV12" : [self._IO,self._FV,self._IV,self._CR,self._NM],
                "IV13" : [self._IO,self._FV,self._TT,self._NM],
                "IV14" : [self._IO,self._RL,self._CR,self._OJ,self._NM],
                "IV15" : [self._IO,self._RL,self._CO,self._OJ,self._NM],
                "IV16" : [self._IO,self._LL,self._CO,self._OJ,self._NM],
                "IV17" : [self._IO,self._LL,self._CR,self._OJ,self._NM],
                "IV18" : [self._IO,self._LB,self._CO,self._NM],
                "IV19" : [self._IO,self._LB,self._CO,self._WM],
                "IV20" : [self._IO,self._LB,self._CO,self._WM_BC],
                "IV21" : [self._IO,self._LB,self._CR,self._NM],
                "IV22" : [self._IO,self._LB,self._CR,self._WM],
                "IV23" : [self._IO,self._LB,self._CR,self._WM_BC],
                "IV24" : [self._IO,self._MX,self._MO,self._OV,self._WM],
                "IV25" : [self._IO,self._MX,self._MO,self._OV,self._WM_BC],
                "IV26" : [self._IO,self._MD,self._MO,self._OV,self._WM],
                "IV27" : [self._IO,self._MD,self._MO,self._OV,self._WM_BC],
                "IV28" : [self._IO,self._GR],
                "IV29" : [self._IO,self._FR],
                "IV30" : [self._IO,self._PA],
        }

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

    def _GR(self,dataset):
        """ Gengival Recession
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

    def _add_teeth(self,dataset,teeth):
        teeth_sequences = []
        for tooth in teeth:
            if ToothCodes.is_valid_tooth_number(tooth):
                teeth_sequences.append(
                    self._get_sct_code_sequence(**ToothCodes.SCT_TOOTH_CODES[tooth]))

        if not hasattr(dataset,'PrimaryAnatomicStructureSequence'):
            dataset.PrimaryAnatomicStructureSequence = Sequence([])

        # I'm not sure if i can use append on a Sequence() object.
        dataset.PrimaryAnatomicStructureSequence.append(teeth_sequences)
