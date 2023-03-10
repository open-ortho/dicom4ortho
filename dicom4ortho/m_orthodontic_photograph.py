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
from dicom4ortho.m_ada1107 import ADA1107

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
    "IV03": [],
    "IV04": [],
    "IV05": [],
    "IV06": [],
    "IV07": [],
    "IV08": [],
    "IV09": [],
    "IV10": [],
    "IV11": [],
    "IV12": [],
    "IV13": [],
    "IV14": [],
    "IV15": [],
    "IV16": [],
    "IV17": [],
    "IV18": [
        '21', '22', '23', '24', '15', '26', '27', '28',
        '31', '32', '33', '34', '35', '36', '37', '38',
    ],
    "IV19": [
        '21', '22', '23', '24', '15', '26', '27', '28',
        '31', '32', '33', '34', '35', '36', '37', '38',
    ],
    "IV20": [],
    "IV21": [],
    "IV22": [],
    "IV23": [],
    "IV24": [],
    "IV25": [],
    "IV26": [],
    "IV27": [],
    "IV28": [],
    "IV29": [],
    "IV30": [],

}


class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        arguments:

        image_type: a 4 digit ortho photo type code as specified in WP-1100. Ex. EV01

        input_image_filename: name of input image file

        output_image_filename: name of output image file
    """
    type_keyword = ""  # Orthodontic View String, e.g. "IV03"
    ada1107_view = None  # Row in ADA-1107 views.csv for this particular view
    teeth = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ada1107 = ADA1107()
        self.teeth = kwargs.get('teeth')
        if kwargs.get('image_type') is not None:
            # Allow for both dash separated and not separated naming
            self.type_keyword = kwargs.get('image_type').replace('-', '')
            self.ada1107_view = self.ada1107.VIEWS.get(self.type_keyword)

    def _get_code_dataset(self, ada1107_code_keyword) -> Dataset:
        """ Construct a DICOM Dataset from a row in the codes.csv of ADA1107 

        ada1107_code must be a dictionary with the following keys:
        code
        codeset
        meaning
        """
        ada1107_code = self.ada1107.CODES.get(ada1107_code_keyword)
        if ada1107_code == None:
            logging.warning(f"Keyword [{ada1107_code_keyword}] did not match any code. Skipping.")
            return None
        code_dataset = Dataset()
        code_dataset.CodeMeaning = ada1107_code.get(
            'meaning')[:64]  # LO only allows 64 characters
        code_dataset.CodeValue = ada1107_code.get('code')
        code_dataset.CodingSchemeDesignator = ada1107_code.get('codeset')
        return code_dataset

    def _get_code_sequence(self, ada1107_code_keyword) -> Sequence:
        code_dataset = self._get_code_dataset(ada1107_code_keyword)
        if code_dataset is None:
            return None
        return Sequence([code_dataset])

    def _set_dicom_attributes(self):
        # Get the array of functions to set this required type.
        logging.debug(f'Setting DICOM attributes for {self.type_keyword}')

        # Make a nice comment from keyword and description
        ImageComments = f"{self.type_keyword}^{self.ada1107_view.get('ImageComments')}"

        # NBSP character OxA0 is not allowed in Image Comments. Replace with a
        # Space (0x20)
        self._ds.ImageComments = ImageComments.replace('\xa0', '\x20')
        self._ds.SeriesDescription = self.ada1107_view.get('SeriesDescription')

        self._ds.PatientOrientation = self.ada1107.CODES.get(
            self.ada1107_view.get('PatientOrientation')).get('code').split('^')
        self._ds.ImageLaterality = self.ada1107.CODES.get(
            self.ada1107_view.get('ImageLaterality')).get('code')

        self.add_device()
        self.add_anatomic_region()
        self.add_primary_anatomic_structure()
        self.add_acquisition_context()
        # self.add_teeth()

    def add_acquisition_context(self):
        AcquisitionContextSequence = Sequence([])
        # Find all columns which start with AcquisitionContextSequence in ada1107_view
        for index, key in enumerate(self.ada1107_view):
            if key.startswith("AcquisitionContextSequence"):
                concept_name = key.split("^")[1]
                concept_name_code_sequence = self._get_code_sequence(
                    concept_name)
                for concept_code in self.ada1107_view.get(key).split("^"):
                    acs_ds = Dataset()
                    acs_ds.ValueType = 'CODE'
                    acs_ds.ConceptNameCodeSequence = concept_name_code_sequence
                    acs_ds.ConceptCodeSequence = self._get_code_sequence(concept_code)
                    AcquisitionContextSequence.append(acs_ds)
        self._ds.AcquisitionContextSequence = AcquisitionContextSequence

    def add_device(self):
        DeviceSequence = Sequence([])
        for device in self.ada1107_view.get('DeviceSequence').split("^"):
            if device != "na" and len(device) > 0:
                DeviceSequence.append(self._get_code_dataset(device))
        # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
        if (len(DeviceSequence) > 0):
            self._ds.DeviceSequence = DeviceSequence

    def add_anatomic_region(self):
        # AnatomicRegionSequence allows for a single value
        self._ds.AnatomicRegionSequence = self._get_code_sequence(
            self.ada1107_view.get('AnatomicRegionSequence'))

        # More than one AnatomicRegionModifierSequence are allowed
        AnatomicRegionModifierSequence = Sequence([])
        for arm in self.ada1107_view.get('AnatomicRegionModifierSequence').split("^"):
            AnatomicRegionModifierSequence.append(self._get_code_dataset(arm))
        # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
        if (len(AnatomicRegionModifierSequence) > 0):
            self._ds.AnatomicRegionSequence[0].AnatomicRegionModifierSequence = AnatomicRegionModifierSequence

    def add_primary_anatomic_structure(self):
        # PrimaryAnatomicStructureSequence allows for multiple values, but currently only one is supported by this code.
        pas = self.ada1107_view.get('PrimaryAnatomicStructureSequence')
        if pas != "na" and len(pas) > 0:
            self._ds.PrimaryAnatomicStructureSequence = self._get_code_sequence(
                pas)

            # More than one AnatomicRegionModifierSequence are allowed
            PrimaryAnatomicStructureModifierSequence = Sequence([])
            for pasm in self.ada1107_view.get('PrimaryAnatomicStructureModifierSequence').split("^"):
                if pasm != "na" and len(pasm) > 0:
                    PrimaryAnatomicStructureModifierSequence.append(
                        self._get_code_dataset(pasm))
            # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
            if (len(PrimaryAnatomicStructureModifierSequence) > 0):
                self._ds.PrimaryAnatomicStructureSequence[
                    0].PrimaryAnatomicStructureModifierSequence = PrimaryAnatomicStructureModifierSequence

    def add_teeth(self):
        teeth = self.teeth
        logging.debug("Adding teeth")
        if teeth == defaults.ADD_MAX_ALLOWED_TEETH:
            logging.debug("Setting all possibly allowed teeth.")
            teeth = ALLOWED_TEETH[self.type_keyword]

        if len(teeth) > 0:
            if not hasattr(self._ds, 'PrimaryAnatomicStructureSequence'):
                self._ds.PrimaryAnatomicStructureSequence = Sequence([])

            for tooth in teeth:
                if ToothCodes.is_valid_tooth_number(tooth):
                    self._ds.PrimaryAnatomicStructureSequence.append(
                        self._get_code_dataset(*ToothCodes.SCT_TOOTH_CODES[tooth]))

    def is_extraoral(self) -> bool:
        if self.type_keyword.startswith("EV"):
            return True
        else:
            return False

    def is_intraoral(self) -> bool:
        if self.type_keyword.startswith("IV"):
            return True
        else:
            return False

    def save(self, filename=None):
        filename = filename or self.output_image_filename
        self.set_image()
        self._set_dicom_attributes()
        self._ds.save_as(filename=filename, write_like_original=False)
        logging.warning(f"File [{filename}] saved.")


class OrthodonticSeries():
    """ Class representing an Orthodontic Photo session.

    Examples of orthodontic series:

    * A set of intra-oral photographs take on the same day for the same appointment.
    * A set of extra-oral photographs take on the same day for the same appointment.

    """
    # SeriesInstanceUID
    UID = None
    StudyUID = None

    Photos = None

    def __init__(self, **kwargs) -> None:
        """ New Orthodontic Series

        :uid: The Series DICOM UID. Defaults to generating a new one.
        :description: The Series Description to add to all photos.
        """
        self.description = kwargs.get("description")
        self.UID = kwargs.get("uid") or defaults.generate_dicom_uid()
        self.Photos = []

    def __len__(self):
        return len(self.Photos)

    def add(self, photo: OrthodonticPhotograph) -> None:
        self.Photos.append(photo)

    def save(self) -> None:
        logging.info(
            f"Requested to save {len(self.Photos)} Photos within Series {self.UID}")
        for photo in self.Photos:
            photo.series_description = self.description
            photo.series_instance_uid = self.UID
            photo.study_instance_uid = self.StudyUID
            photo.save()


class OrthodonticStudy():
    """ Class representing an Orthodontic Photo visit.

    Examples of orthodontic study:

    * As part of the same appointment/visit/encounter, the staff takes intraoral and extraoral photographs of the patient. While the intraoral and the extra oral are in separate series, they are both part of the same study.
    * During the same day an X-Ray is taken, that would go in a separate Study.

    """
    # SeriesInstanceUID
    UID = None
    Series = None

    def __init__(self, **kwargs) -> None:
        """ New Orthodontic Study

        :uid: The Series DICOM UID. Defaults to generating a new one.
        :description: The Study Description to add to all photos.
        """
        self.UID = kwargs.get("uid") or defaults.generate_dicom_uid()
        self.Series = []

    def __len__(self):
        return len(self.Series)

    def add(self, serie: OrthodonticSeries) -> None:
        serie.StudyUID = self.UID
        self.Series.append(serie)

    def save(self) -> None:
        logging.info(
            f"Requested to save {len(self.Series)} Series within Study {self.UID}")
        for serie in self.Series:
            serie.save()
