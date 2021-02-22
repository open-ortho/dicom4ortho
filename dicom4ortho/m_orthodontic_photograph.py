# pylint: disable=invalid-name
''' Orthodontic Photograph Classes.

Adds SNOMED CT codes in DICOM object for Orthodontic Views.

'''

import logging
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset

from dicom4ortho.model import PhotographBase
import dicom4ortho.m_tooth_codes as ToothCodes
from dicom4ortho import defaults


def _EO(dataset):
    # Here we assume all extraoral images to be unpaired. Pairing should be
    # set at a higher level: only the operator knows if they will be
    # collecting a pair or not.
    dataset.ImageLaterality = 'U'


def _IO(dataset):
    # Here we assume all extraoral images to be unpaired. Pairing should be
    # set at a higher level: only the operator knows if they will be
    # collecting a pair or not.
    dataset.ImageLaterality = 'U'


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
    dataset.ImageView = _get_sct_code_sequence(
        '789135000','Mirrored view uncorrected')

def _WM_BC(dataset):
    """ With Mirror But Corrected

    flipped and/or rotated to appear as if it has been taken directly
    without a mirror used for intraoral photographs only. Does not apply
    to extraoral photographs
    """
    dataset.ImageView = _get_sct_code_sequence(
        '787610003','Mirror corrected')


def _NM(dataset):
    """ No Mirror
    """
    dataset.ImageView = _get_sct_code_sequence(
        '255589003','Direct')


def _RB(dataset):
    """ Right Buccal

    used to document posterior occlusion
    """
    _jaw_region(dataset)
    dataset.AcquisitionView = _get_sct_code_sequence(
        '30730003', 'Sagittal (qualifier value)')
    dataset.FunctionalCondition = _get_sct_code_sequence(
        '286866000', 'Mouth Closed')
    dataset.PatientOrientation = ['A', 'F']  # Anterior, Foot


def _LB(dataset):
    """ Left Buccal

    used to document posterior occlusion
    """
    _jaw_region(dataset)
    dataset.AcquisitionView = _get_sct_code_sequence(
        '30730003', 'Sagittal (qualifier value)')
    dataset.FunctionalCondition = _get_sct_code_sequence(
        '286866000', 'Mouth Closed')
    dataset.PatientOrientation = ['P', 'F']  # Anterior, Foot


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

def _jaw_region(dataset):
    a_r_s = _get_sct_code_sequence(
        '181811001', 'Jaw Region')
    a_r_s[0].AnatomicRegionModifierSequence = _null()
    dataset.AnatomicRegionSequence = a_r_s

def _get_sct_code_dataset(value, meaning):
    code_dataset = Dataset()
    code_dataset.CodeMeaning = meaning
    code_dataset.CodeValue = value
    code_dataset.CodingSchemeDesignator = 'SCT'
    return code_dataset

def _get_sct_code_sequence(value, meaning):
    return Sequence([_get_sct_code_dataset(value, meaning)])


IMAGE_TYPES = {
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

    "IV01": [_IO, _RB, _CO, _NM],
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

ALLOWED_TEETH = {
    "EV01": [],
    "EV02": [],
    "EV03": [],
    "EV04": [],
    "EV05": [],
    "EV06": [],
    "EV07": [],
    "EV08": [],
    "EV09": [],
    "EV10": [],
    "EV11": [],
    "EV12": [],
    "EV13": [],
    "EV14": [],
    "EV15": [],
    "EV16": [],
    "EV17": [],
    "EV18": [],
    "EV19": [],
    "EV20": [],
    "EV21": [],
    "EV22": [],
    "EV23": [],
    "EV24": [],
    "EV25": [],
    "EV26": [],
    "EV27": [],
    "EV28": [],
    "EV29": [],
    "EV30": [],
    "EV31": [],
    "EV32": [],
    "EV33": [],
    "EV34": [],
    "EV35": [],
    "EV36": [],
    "EV37": [],
    "EV38": [],
    "EV39": [],
    "EV40": [],
    "EV41": [],
    "EV42": [],
    "EV43": [],

    "IV01": [
        '11', '12', '13', '14', '15', '16', '17', '18',
        '41', '42', '43', '44', '45', '46', '47', '48',
    ],
    "IV02": [
        '11', '12', '13', '14', '15', '16', '17', '18',
        '41', '42', '43', '44', '45', '46', '47', '48',
    ],
    "IV03": [ ],
    "IV04": [ ],
    "IV05": [ ],
    "IV06": [ ],
    "IV07": [ ],
    "IV08": [ ],
    "IV09": [ ],
    "IV10": [ ],
    "IV11": [ ],
    "IV12": [ ],
    "IV13": [ ],
    "IV14": [ ],
    "IV15": [ ],
    "IV16": [ ],
    "IV17": [ ],
    "IV18": [
        '21', '22', '23', '24', '15', '26', '27', '28',
        '31', '32', '33', '34', '35', '36', '37', '38',
    ],
    "IV19": [
        '21', '22', '23', '24', '15', '26', '27', '28',
        '31', '32', '33', '34', '35', '36', '37', '38',
    ],
    "IV20": [ ],
    "IV21": [ ],
    "IV22": [ ],
    "IV23": [ ],
    "IV24": [ ],
    "IV25": [ ],
    "IV26": [ ],
    "IV27": [ ],
    "IV28": [ ],
    "IV29": [ ],
    "IV30": [ ],

}


class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        arguments:

        image_type: a 4 digit ortho photo type code as specified in WP-1100. Ex. EV01

        input_image_filename: name of input image file

        output_image_filename: name of output image file
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if callable(kwargs['image_type']):
            # If a custom function was passed, then use it.
            self._type = kwargs['image_type']
        else:
            # Otherwise we shall look up the tags to add based on the function
            # defined in OrthodontiPhotographTypes
            # Allow for both dash separated and not separated naming
            self.image_type = kwargs['image_type'].replace('-', '')

            # Get the array of functions to set this required type.
            self._type = (IMAGE_TYPES[self.image_type])

        if "teeth" in kwargs:
            self.add_teeth(kwargs['teeth'])
        self._set_dicom_attributes()

    def _set_dicom_attributes(self):
        for set_attr in self._type:
            logging.debug('Setting DICOM attributes for {}', self._type)
            set_attr(self._ds)

    def add_teeth(self, teeth):
        logging.debug("Adding teeth")
        if teeth == defaults.ADD_MAX_ALLOWED_TEETH:
            logging.debug("Setting all possibly allowed teeth.")
            teeth = ALLOWED_TEETH[self.image_type]

        if len(teeth) > 0:
            if not hasattr(self._ds, 'PrimaryAnatomicStructureSequence'):
                self._ds.PrimaryAnatomicStructureSequence = Sequence([])

            for tooth in teeth:
                if ToothCodes.is_valid_tooth_number(tooth):
                    self._ds.PrimaryAnatomicStructureSequence.append(
                        _get_sct_code_dataset(*ToothCodes.SCT_TOOTH_CODES[tooth]))

