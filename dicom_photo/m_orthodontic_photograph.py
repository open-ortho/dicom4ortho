# pylint: disable=invalid-name
''' Orthodontic Photograph Classes.

Adds SNOMED CT codes in DICOM object for Orthodontic Views.

'''

import logging
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

from dicom_photo.model import PhotographBase
import dicom_photo.m_tooth_codes as ToothCodes


def _EO(dataset):
    # Here we assume all extraoral images to be unpaired. Pairing should be
    # set at a higher level: only the operator knows if they will be
    # collecting a pair or not.
    dataset.ImageLaterality = 'U'

def _IO(dataset):
    pass

def _RP(dataset):
    """ Right Profile
    """
    _face(dataset)
    dataset.AcquisitionView = _get_sct_code_sequence(
        '30730003', 'Sagittal (qualifier value)')
    dataset.PatientOrientation = ['A', 'F']  # Anterior, Foot

def _LP(dataset):
    """ Left Profile
    """
    _face(dataset)
    dataset.PatientOrientation = ['P', 'F']  # Anterior, Foot

def _FF(dataset):
    _face(dataset)
    dataset.PatientOrientation = ['R', 'F']  # Right, Foot

def _FS(dataset):
    """ Full Smile
    """
    _face(dataset)
    dataset.PatientOrientation = ['R', 'F']  # Right, Foot

def _LC(dataset):
    """ Lips Closed
    """
    dataset.FunctionalCondition = _get_sct_code_sequence(
        '787607005', 'Lips closed')

def _LR(dataset):
    """ Lips Relaxed
    """
    dataset.FunctionalCondition = _get_sct_code_sequence(
        '745165', 'Lips relaxed')

def _CO(dataset):
    dataset.OcclusalRelationship = _get_sct_code_sequence('110320000',
                                                                'Centric occlusion (observable entity)')

def _CR(dataset):
    dataset.OcclusalRelationship = _get_sct_code_sequence('736783005',
                                                                'Centric relation (observable entity)')

def _or_none(dataset):
    """ Null Occlusal Relationship
    """
    dataset.OcclusalRelationship = _null()

def _MD(dataset):
    """ Mandibular
    """
    a_r_s = _get_sct_code_sequence(
        '181812008', 'Entire mandible (body structure)')
    a_r_s[0].AnatomicRegionModifierSequence = _null()
    dataset.AnatomicRegionSequence = a_r_s

def _MX(dataset):
    """ Maxillary
    """
    pass

def _MO(dataset):
    """ Mouth Open
    """
    pass

def _TA(dataset):
    """ Teeth Apart
    """
    pass

def _OJ(dataset):
    """ Showing Overjet
    """
    pass

def _PF(dataset):
    """ Mandible Postured Forward
    """
    dataset.FunctionalCondition = _get_sct_code_sequence('787611004',
                                                                'Photographic image extraoral with mandible postured forward (record artifact)')

def _OF(dataset):
    """ Other Face

    some other view of the face; e.g., with the face tipped back, or from
    above
    """
    pass

def _WM(dataset):
    """ With Mirror

    used for intraoral photographs only. Does not apply to extraoral
    photographs
    """
    pass

def _WM_BC(dataset):
    """ With Mirror But Corrected

    flipped and/or rotated to appear as if it has been taken directly
    without a mirror used for intraoral photographs only. Does not apply
    to extraoral photographs
    """
    pass

def _NM(dataset):
    """ No Mirror
    """
    pass

def _RB(dataset):
    """ Right Buccal

    used to document posterior occlusion
    """
    pass

def _LB(dataset):
    """ Left Buccal

    used to document posterior occlusion
    """
    pass

def _RL(dataset):
    """ Right Lateral

    used to document the dental occlusion from the subject's right side
    """
    pass

def _LL(dataset):
    """ Left Buccal

    used to document the dental occlusion from the subject's left side
    """
    pass

def _FV(dataset):
    """ Frontal View
    """
    pass

def _IV(dataset):
    """ Inferior View

    use IO.IV to show depth of bite and overjet from below
    """
    pass

def _SV(dataset):
    """ Superior View
    """
    pass

def _45(dataset):
    """ 45º View
    """
    dataset.AcquisitionView = _get_sct_code_sequence('30730003',
                                                            'Photographic image extraoral with 45 degree view (record artifact)')

def _OV(dataset):
    """ Occlusal View
    """
    pass

def _CS(dataset):
    """ Close-up Smile
    """
    pass

def _OC(dataset):
    """ Occlusal Cant
    """
    pass

def _FI(dataset):
    """ Forensic Interest
    """
    pass

def _NW(dataset):
    """ Nerve Weakness
    """
    pass

def _AN(dataset):
    """ Anomalies
    """
    pass

def _FR(dataset):
    """ Frenum
    """
    pass

def _PA(dataset):
    """ Using Photo Accessory

    such as a photo contraster providing a solid background or black
    mirror. Can be appended to any intraoral (IO) view code as needed
    """
    pass

def _TT(dataset):
    """ Tongue Thrust
    """
    pass

def _IN(dataset):
    """ Initial

    refers to Initial time point, generally observation or pre-treatment
    """
    pass

def _P(dataset):
    """ Progress

    refers to Progress time point, i.e. progress photos
    """
    pass

def _F(dataset):
    """ Final

    refers to Final time point, generally when treatment is finished
    """
    pass

def _FU(dataset):
    """ Follow-Up

    refers to Follow-Up time point, generally taken to show
    post-treatment changes
    """
    pass

def _GR(dataset):
    """ Gengival Recession
    """
    pass

def _null():
    return _get_sct_code_sequence('276727009', 'Null (qualifier value)')

def _mandible(dataset):
    a_r_s = _get_sct_code_sequence(
        '181812008', 'Entire mandible (body structure)')
    a_r_s[0].AnatomicRegionModifierSequence = _null()
    dataset.AnatomicRegionSequence = a_r_s

def _face(dataset):
    a_r_s = _get_sct_code_sequence(
        '302549007', 'Entire face (body structure)')
    a_r_s[0].AnatomicRegionModifierSequence = _null()
    dataset.AnatomicRegionSequence = a_r_s

def _get_sct_code_sequence(value, meaning):
    code_dataset = Dataset()
    code_dataset.CodeMeaning = meaning
    code_dataset.CodeValue = value
    code_dataset.CodingSchemeDesignator = 'SCT'
    return Sequence([code_dataset])

IMAGE_TYPES ={
            "EV01": [_EO, _RP, _LR, _CO],
            "EV02": [_EO, _RP, _LR, _CR],
            "EV03": [_EO, _RP, _LC, _CO],
            "EV04": [_EO, _RP, _LC, _CR],
            "EV05": [_EO, _RP, _FS, _CO],
            "EV06": [_EO, _RP, _FS, _CR],
            "EV07": [_EO, _RP, _PF, _or_none],
            "EV08": [_EO, _RP, _LR, _CO, _45],
            "EV09": [_EO, _RP, _LR, _CR, _45],
            "EV10": [_EO, _LP, _LC, _CO, _45],
            "EV11": [_EO, _RP, _LC, _CR, _45],
            "EV12": [_EO, _RP, _FS, _CO, _45],
            "EV13": [_EO, _RP, _FS, _CR, _45],
            "EV14": [_EO, _RP, _PF, _45],
            "EV15": [_EO, _FF, _LR, _CO],
            "EV16": [_EO, _FF, _LR, _CR],
            "EV17": [_EO, _FF, _LC, _CO],
            "EV18": [_EO, _FF, _LC, _CR],
            "EV19": [_EO, _FF, _FS, _CO],
            "EV20": [_EO, _FF, _FS, _CR],
            "EV21": [_EO, _FF, _PF],
            "EV22": [_EO, _LP, _LR, _CO],
            "EV23": [_EO, _LP, _LR, _CR],
            "EV24": [_EO, _LP, _LC, _CO],
            "EV25": [_EO, _LC, _LC, _CR],
            "EV26": [_EO, _LP, _FS, _CO],
            "EV27": [_EO, _LP, _FS, _CR],
            "EV28": [_EO, _LP, _FS],
            "EV29": [_EO, _LP, _LR, _CO, _45],
            "EV30": [_EO, _LP, _LC, _CR, _45],
            "EV31": [_EO, _LP, _LC, _CO, _45],
            "EV32": [_EO, _LP, _LC, _CR, _45],
            "EV33": [_EO, _LP, _FS, _CO, _45],
            "EV34": [_EO, _LP, _FS, _CR, _45],
            "EV35": [_EO, _LP, _PF, _45],
            "EV36": [_EO, _OF, _IV],
            "EV37": [_EO, _OF, _SV],
            "EV38": [_EO, _OF, _CS],
            "EV39": [_EO, _OF, _OC],
            "EV40": [_EO, _OF, _FI],
            "EV41": [_EO, _OF, _AN],
            "EV42": [_EO, _FF, _MO],
            "EV43": [_EO, _FF, _NW],

            "IV01": [_IO, _RB, _CO],
            "IV02": [_IO, _RB, _CO, _WM],
            "IV03": [_IO, _RB, _CO, _WM_BC],
            "IV04": [_IO, _RB, _CR, _NM],
            "IV05": [_IO, _RB, _CR, _WM],
            "IV06": [_IO, _RB, _CR, _WM_BC],
            "IV07": [_IO, _FV, _CO, _NM],
            "IV08": [_IO, _FV, _CR, _NM],
            "IV09": [_IO, _FV, _TA, _NM],
            "IV10": [_IO, _FV, _MO, _NM],
            "IV11": [_IO, _FV, _IV, _CO, _NM],
            "IV12": [_IO, _FV, _IV, _CR, _NM],
            "IV13": [_IO, _FV, _TT, _NM],
            "IV14": [_IO, _RL, _CR, _OJ, _NM],
            "IV15": [_IO, _RL, _CO, _OJ, _NM],
            "IV16": [_IO, _LL, _CO, _OJ, _NM],
            "IV17": [_IO, _LL, _CR, _OJ, _NM],
            "IV18": [_IO, _LB, _CO, _NM],
            "IV19": [_IO, _LB, _CO, _WM],
            "IV20": [_IO, _LB, _CO, _WM_BC],
            "IV21": [_IO, _LB, _CR, _NM],
            "IV22": [_IO, _LB, _CR, _WM],
            "IV23": [_IO, _LB, _CR, _WM_BC],
            "IV24": [_IO, _MX, _MO, _OV, _WM],
            "IV25": [_IO, _MX, _MO, _OV, _WM_BC],
            "IV26": [_IO, _MD, _MO, _OV, _WM],
            "IV27": [_IO, _MD, _MO, _OV, _WM_BC],
            "IV28": [_IO, _GR],
            "IV29": [_IO, _FR],
            "IV30": [_IO, _PA],
        }

class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        arguments:

        photo_type: a 4 digit ortho photo type code as specified in WP-1100. Ex. EV01

        input_image_filename: name of input image file

        output_image_filename: name of output image file
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        if callable(kwargs['photo_type']):
            # If a custom function was passed, then use it.
            self._type = kwargs['photo_type']
        else:
            # Otherwise we shall look up the tags to add based on the function
            # defined in OrthodontiPhotographTypes
            # Allow for both dash separated and not separated naming
            photo_type = kwargs['photo_type'].replace('-','')

            # Get the array of functions to set this required type.
            self._type = (IMAGE_TYPES[photo_type])

        self._set_dicom_attributes()

    def _set_dicom_attributes(self):
        for set_attr in self._type:
            logging.debug('Setting DICOM attributes for {}', self._type)
            set_attr(self._ds)

    def add_teeth(self, teeth):
        teeth_sequences = []
        for tooth in teeth:
            if ToothCodes.is_valid_tooth_number(tooth):
                teeth_sequences.append(
                    _get_sct_code_sequence(**ToothCodes.SCT_TOOTH_CODES[tooth]))

        if not hasattr(self._ds, 'PrimaryAnatomicStructureSequence'):
            self._ds.PrimaryAnatomicStructureSequence = Sequence([])

        # I'm not sure if i can use append on a Sequence() object.
        self._ds.PrimaryAnatomicStructureSequence.append(teeth_sequences)


# class OrthodonticPhotographTypes(object):
#     ''' Orthodontic Photograph Types as defined in ADA WP-1100

#     Naming convention: types are prefixes wit an underscore to indicate that
#     these are private types, with the additional benefit that the term 45 can
#     follow the same convention. Python does not allow variable or function
#     names to start with a digit.

#     If teeth are present, add them in a list as strings using ISO tooth
#     numbering convention. Example:

#     opt = OrthodonticPhotographTypes(teeth=['24','25','26','27','28','34','35','36','37','38'])
#     '''

#     def __init__(self,teeth=[]):
#         self.views = {
#             "EV01": [self._EO, self._RP, self._LR, self._CO],
#             "EV02": [self._EO, self._RP, self._LR, self._CR],
#             "EV03": [self._EO, self._RP, self._LC, self._CO],
#             "EV04": [self._EO, self._RP, self._LC, self._CR],
#             "EV05": [self._EO, self._RP, self._FS, self._CO],
#             "EV06": [self._EO, self._RP, self._FS, self._CR],
#             "EV07": [self._EO, self._RP, self._PF, self._or_none],
#             "EV08": [self._EO, self._RP, self._LR, self._CO, self._45],
#             "EV09": [self._EO, self._RP, self._LR, self._CR, self._45],
#             "EV10": [self._EO, self._LP, self._LC, self._CO, self._45],
#             "EV11": [self._EO, self._RP, self._LC, self._CR, self._45],
#             "EV12": [self._EO, self._RP, self._FS, self._CO, self._45],
#             "EV13": [self._EO, self._RP, self._FS, self._CR, self._45],
#             "EV14": [self._EO, self._RP, self._PF, self._45],
#             "EV15": [self._EO, self._FF, self._LR, self._CO],
#             "EV16": [self._EO, self._FF, self._LR, self._CR],
#             "EV17": [self._EO, self._FF, self._LC, self._CO],
#             "EV18": [self._EO, self._FF, self._LC, self._CR],
#             "EV19": [self._EO, self._FF, self._FS, self._CO],
#             "EV20": [self._EO, self._FF, self._FS, self._CR],
#             "EV21": [self._EO, self._FF, self._PF],
#             "EV22": [self._EO, self._LP, self._LR, self._CO],
#             "EV23": [self._EO, self._LP, self._LR, self._CR],
#             "EV24": [self._EO, self._LP, self._LC, self._CO],
#             "EV25": [self._EO, self._LC, self._LC, self._CR],
#             "EV26": [self._EO, self._LP, self._FS, self._CO],
#             "EV27": [self._EO, self._LP, self._FS, self._CR],
#             "EV28": [self._EO, self._LP, self._FS],
#             "EV29": [self._EO, self._LP, self._LR, self._CO, self._45],
#             "EV30": [self._EO, self._LP, self._LC, self._CR, self._45],
#             "EV31": [self._EO, self._LP, self._LC, self._CO, self._45],
#             "EV32": [self._EO, self._LP, self._LC, self._CR, self._45],
#             "EV33": [self._EO, self._LP, self._FS, self._CO, self._45],
#             "EV34": [self._EO, self._LP, self._FS, self._CR, self._45],
#             "EV35": [self._EO, self._LP, self._PF, self._45],
#             "EV36": [self._EO, self._OF, self._IV],
#             "EV37": [self._EO, self._OF, self._SV],
#             "EV38": [self._EO, self._OF, self._CS],
#             "EV39": [self._EO, self._OF, self._OC],
#             "EV40": [self._EO, self._OF, self._FI],
#             "EV41": [self._EO, self._OF, self._AN],
#             "EV42": [self._EO, self._FF, self._MO],
#             "EV43": [self._EO, self._FF, self._NW],

#             "IV01": [self._IO, self._RB, self._CO],
#             "IV02": [self._IO, self._RB, self._CO, self._WM],
#             "IV03": [self._IO, self._RB, self._CO, self._WM_BC],
#             "IV04": [self._IO, self._RB, self._CR, self._NM],
#             "IV05": [self._IO, self._RB, self._CR, self._WM],
#             "IV06": [self._IO, self._RB, self._CR, self._WM_BC],
#             "IV07": [self._IO, self._FV, self._CO, self._NM],
#             "IV08": [self._IO, self._FV, self._CR, self._NM],
#             "IV09": [self._IO, self._FV, self._TA, self._NM],
#             "IV10": [self._IO, self._FV, self._MO, self._NM],
#             "IV11": [self._IO, self._FV, self._IV, self._CO, self._NM],
#             "IV12": [self._IO, self._FV, self._IV, self._CR, self._NM],
#             "IV13": [self._IO, self._FV, self._TT, self._NM],
#             "IV14": [self._IO, self._RL, self._CR, self._OJ, self._NM],
#             "IV15": [self._IO, self._RL, self._CO, self._OJ, self._NM],
#             "IV16": [self._IO, self._LL, self._CO, self._OJ, self._NM],
#             "IV17": [self._IO, self._LL, self._CR, self._OJ, self._NM],
#             "IV18": [self._IO, self._LB, self._CO, self._NM],
#             "IV19": [self._IO, self._LB, self._CO, self._WM],
#             "IV20": [self._IO, self._LB, self._CO, self._WM_BC],
#             "IV21": [self._IO, self._LB, self._CR, self._NM],
#             "IV22": [self._IO, self._LB, self._CR, self._WM],
#             "IV23": [self._IO, self._LB, self._CR, self._WM_BC],
#             "IV24": [self._IO, self._MX, self._MO, self._OV, self._WM],
#             "IV25": [self._IO, self._MX, self._MO, self._OV, self._WM_BC],
#             "IV26": [self._IO, self._MD, self._MO, self._OV, self._WM],
#             "IV27": [self._IO, self._MD, self._MO, self._OV, self._WM_BC],
#             "IV28": [self._IO, self._GR],
#             "IV29": [self._IO, self._FR],
#             "IV30": [self._IO, self._PA],
#         }

#     def _EO(self, dataset):
#         # Here we assume all extraoral images to be unpaired. Pairing should be
#         # set at a higher level: only the operator knows if they will be
#         # collecting a pair or not.
#         dataset.ImageLaterality = 'U'

#     def _IO(self, dataset):
#         pass

#     def _RP(self, dataset):
#         """ Right Profile
#         """
#         self._face(dataset)
#         dataset.AcquisitionView = self._get_sct_code_sequence(
#             '30730003', 'Sagittal (qualifier value)')
#         dataset.PatientOrientation = ['A', 'F']  # Anterior, Foot

#     def _LP(self, dataset):
#         """ Left Profile
#         """
#         self._face(dataset)
#         dataset.PatientOrientation = ['P', 'F']  # Anterior, Foot

#     def _FF(self, dataset):
#         self._face(dataset)
#         dataset.PatientOrientation = ['R', 'F']  # Right, Foot

#     def _FS(self, dataset):
#         """ Full Smile
#         """
#         self._face(dataset)
#         dataset.PatientOrientation = ['R', 'F']  # Right, Foot

#     def _LC(self, dataset):
#         """ Lips Closed
#         """
#         dataset.FunctionalCondition = self._get_sct_code_sequence(
#             '787607005', 'Lips closed')

#     def _LR(self, dataset):
#         """ Lips Relaxed
#         """
#         dataset.FunctionalCondition = self._get_sct_code_sequence(
#             '745165', 'Lips relaxed')

#     def _CO(self, dataset):
#         dataset.OcclusalRelationship = self._get_sct_code_sequence('110320000',
#                                                                    'Centric occlusion (observable entity)')

#     def _CR(self, dataset):
#         dataset.OcclusalRelationship = self._get_sct_code_sequence('736783005',
#                                                                    'Centric relation (observable entity)')

#     def _or_none(self, dataset):
#         """ Null Occlusal Relationship
#         """
#         dataset.OcclusalRelationship = self._null()

#     def _MD(self, dataset):
#         """ Mandibular
#         """
#         a_r_s = self._get_sct_code_sequence(
#             '181812008', 'Entire mandible (body structure)')
#         a_r_s[0].AnatomicRegionModifierSequence = self._null()
#         dataset.AnatomicRegionSequence = a_r_s

#     def _MX(self, dataset):
#         """ Maxillary
#         """
#         pass

#     def _MO(self, dataset):
#         """ Mouth Open
#         """
#         pass

#     def _TA(self, dataset):
#         """ Teeth Apart
#         """
#         pass

#     def _OJ(self, dataset):
#         """ Showing Overjet
#         """
#         pass

#     def _PF(self, dataset):
#         """ Mandible Postured Forward
#         """
#         dataset.FunctionalCondition = self._get_sct_code_sequence('787611004',
#                                                                   'Photographic image extraoral with mandible postured forward (record artifact)')

#     def _OF(self, dataset):
#         """ Other Face

#         some other view of the face; e.g., with the face tipped back, or from
#         above
#         """
#         pass

#     def _WM(self, dataset):
#         """ With Mirror

#         used for intraoral photographs only. Does not apply to extraoral
#         photographs
#         """
#         pass

#     def _WM_BC(self, dataset):
#         """ With Mirror But Corrected

#         flipped and/or rotated to appear as if it has been taken directly
#         without a mirror used for intraoral photographs only. Does not apply
#         to extraoral photographs
#         """
#         pass

#     def _NM(self, dataset):
#         """ No Mirror
#         """
#         pass

#     def _RB(self, dataset):
#         """ Right Buccal

#         used to document posterior occlusion
#         """
#         pass

#     def _LB(self, dataset):
#         """ Left Buccal

#         used to document posterior occlusion
#         """
#         pass

#     def _RL(self, dataset):
#         """ Right Lateral

#         used to document the dental occlusion from the subject's right side
#         """
#         pass

#     def _LL(self, dataset):
#         """ Left Buccal

#         used to document the dental occlusion from the subject's left side
#         """
#         pass

#     def _FV(self, dataset):
#         """ Frontal View
#         """
#         pass

#     def _IV(self, dataset):
#         """ Inferior View

#         use IO.IV to show depth of bite and overjet from below
#         """
#         pass

#     def _SV(self, dataset):
#         """ Superior View
#         """
#         pass

#     def _45(self, dataset):
#         """ 45º View
#         """
#         dataset.AcquisitionView = self._get_sct_code_sequence('30730003',
#                                                               'Photographic image extraoral with 45 degree view (record artifact)')

#     def _OV(self, dataset):
#         """ Occlusal View
#         """
#         pass

#     def _CS(self, dataset):
#         """ Close-up Smile
#         """
#         pass

#     def _OC(self, dataset):
#         """ Occlusal Cant
#         """
#         pass

#     def _FI(self, dataset):
#         """ Forensic Interest
#         """
#         pass

#     def _NW(self, dataset):
#         """ Nerve Weakness
#         """
#         pass

#     def _AN(self, dataset):
#         """ Anomalies
#         """
#         pass

#     def _FR(self, dataset):
#         """ Frenum
#         """
#         pass

#     def _PA(self, dataset):
#         """ Using Photo Accessory

#         such as a photo contraster providing a solid background or black
#         mirror. Can be appended to any intraoral (IO) view code as needed
#         """
#         pass

#     def _TT(self, dataset):
#         """ Tongue Thrust
#         """
#         pass

#     def _IN(self, dataset):
#         """ Initial

#         refers to Initial time point, generally observation or pre-treatment
#         """
#         pass

#     def _P(self, dataset):
#         """ Progress

#         refers to Progress time point, i.e. progress photos
#         """
#         pass

#     def _F(self, dataset):
#         """ Final

#         refers to Final time point, generally when treatment is finished
#         """
#         pass

#     def _FU(self, dataset):
#         """ Follow-Up

#         refers to Follow-Up time point, generally taken to show
#         post-treatment changes
#         """
#         pass

#     def _GR(self, dataset):
#         """ Gengival Recession
#         """
#         pass

#     def _null(self):
#         return self._get_sct_code_sequence('276727009', 'Null (qualifier value)')

#     def _mandible(self, dataset):
#         a_r_s = self._get_sct_code_sequence(
#             '181812008', 'Entire mandible (body structure)')
#         a_r_s[0].AnatomicRegionModifierSequence = self._null()
#         dataset.AnatomicRegionSequence = a_r_s

#     def _face(self, dataset):
#         a_r_s = self._get_sct_code_sequence(
#             '302549007', 'Entire face (body structure)')
#         a_r_s[0].AnatomicRegionModifierSequence = self._null()
#         dataset.AnatomicRegionSequence = a_r_s

#     def _get_sct_code_sequence(self, value, meaning):
#         code_dataset = Dataset()
#         code_dataset.CodeMeaning = meaning
#         code_dataset.CodeValue = value
#         code_dataset.CodingSchemeDesignator = 'SCT'
#         return Sequence([code_dataset])
