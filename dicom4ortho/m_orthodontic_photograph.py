# pylint: disable=invalid-name
''' Orthodontic Photograph Classes.

Adds SNOMED CT codes in DICOM object for Orthodontic Views.

'''

from typing import List, Optional
from datetime import datetime
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset
from dicom4ortho.config import VL_DENTAL_VIEW_CID, DICOM4ORTHO_ROOT_UID, DATE_FORMAT

from dicom4ortho.model import PhotographBase
from dicom4ortho.config import IMPORT_DATE_FORMAT, SeriesInstanceUID_ROOT, StudyInstanceUID_ROOT
from dicom4ortho.utils import generate_dicom_uid
from dicom4ortho.m_dent_oip import DENT_OIP

import logging
logger = logging.getLogger(__name__)


class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        arguments:

        image_type: a 4 digit ortho photo type code as specified in WP-1100. Ex. EV01

        input_image_filename: name of input image file

        output_image_filename: name of output image file
    """

    @property
    def image_type_code_dataset(self) -> Optional[Dataset]:
        """
        The code Dataset that defines this image type.
        """
        return self.get_image_type_code_dataset(self._ds)

    @image_type_code_dataset.setter
    def image_type_code_dataset(self, code_dataset: Dataset):
        """
        The code Dataset that defines this image type.
        """
        self.set_image_type_code_dataset(self._ds, code_dataset)

    def __init__(self, **metadata):
        super().__init__(**metadata)

        # Initialize local variables
        self.type_keyword = ""  # Orthodontic View String, e.g. "IV03"
        self.dent_oip_view = None  # Row in DENT-OIP views.csv for this particular view
        self.treatment_event_type = None
        self.days_after_event = None
        self.dent_oip = DENT_OIP()

        patient_birthdate = metadata.get('patient_birthdate')
        if patient_birthdate is not None:
            try:
                self.patient_birthdate = datetime.strptime(
                    patient_birthdate, IMPORT_DATE_FORMAT).date()
            except (ValueError, TypeError):
                logger.warning("Invalid Patient Birthdate provided.")

        self.study_instance_uid = metadata.get('study_instance_uid')
        self.study_description = metadata.get('study_description')
        self.series_instance_uid = metadata.get('series_instance_uid')
        self.series_description = metadata.get('series_description')
        self.patient_firstname = metadata.get('patient_firstname', '')
        self.patient_lastname = metadata.get('patient_lastname', '')
        self.patient_id = metadata.get('patient_id', '')
        self.patient_sex = metadata.get('patient_sex', '')
        self.dental_provider_firstname = metadata.get(
            'dental_provider_firstname', '')
        self.dental_provider_lastname = metadata.get(
            'dental_provider_lastname', '')
        self.equipment_manufacturer = metadata.get('manufacturer')
        self.treatment_event_type = metadata.get('treatment_event_type')
        self.days_after_event = metadata.get('days_after_event')

        self.set_dicom_attributes_by_type_keyword(metadata.get('image_type'))

        # TODO: extract this to a higher level to give the user the ability to set it when needed.
        # See https://github.com/open-ortho/dicom4ortho/issues/16
        self._ds.BurnedInAnnotation = metadata.get(
            'burned_in_annotation', 'NO')

        # this hardcoding might not be ideal here. But for all orthodontic photography purposes that i am aware of, this is always DSC. These could come from EXIF. See https://dicom.nema.org/medical/dicom/current/output/chtml/part17/chapter_NNNN.html but they might not. The code here should
        # Digital Still Camera (DSC): direct image capture
        self._ds.SceneType = 1
        self._ds.FileSource = 3  # Digital Still Camera (DSC)

        # TODO: extract this to a higher level to give the user the ability to set it when needed.
        # Use when the staff is taking test shots. Then it is not expected for the view in question to actually show the correct view for the patient.
        # See http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.12.html#sect_C.7.6.12 . In these cases, the Phantom would have to go in the Device Sequence. For regular usage, we should safely be able to set this to 'NO'.
        # See https://github.com/open-ortho/dicom4ortho/issues/15
        self._ds.QualityControlImage = 'NO'

    @staticmethod
    def get_image_type_code_dataset(ds: Dataset) -> Optional[Dataset]:
        """
        Get the code that defines this image type.

        Returns the first code item from ViewCodeSequence with the Context
        Identifier (CID) VL_DENTAL_VIEW_CID and Context Group Extension Flag set
        to 'Y'. 

        As defined in DENT-OIP. See that for more information.
        """
        view_seq = getattr(ds, 'ViewCodeSequence', None)
        if not view_seq:
            logger.warning(
                "Cannot identify this image: ViewCodeSequence not present.")
            return None
        for item in view_seq:
            if (
                getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                getattr(item, 'ContextGroupExtensionFlag', None) == 'Y'
            ):
                return item
        logger.warning(
            "No ViewCodeSequence item with proprietary ContextIdentifier and extension flag found.")
        return None

    @staticmethod
    def set_image_type_code_dataset(ds: Dataset, code_dataset: Dataset, creator_uid: str = None) -> None:
        """
        Set the code that defines this image type.

        Adds Context Group Extension attributes as required by DICOM for private
        codes.  Only the code Dataset with the proprietary CID and extension
        flag is set or replaced; others are preserved.

        This function modifies the given Dataset in place and does not return a value.

        As defined in DENT-OIP. See that for more information.

        :param ds: The DICOM Dataset to modify
        :param code_dataset: The code Dataset to insert/update
        :param creator_uid: (optional) The ContextGroupExtensionCreatorUID to use. If not provided, will use code_dataset's value if set, else fallback to DICOM4ORTHO_ROOT_UID with a warning.
        """
        if code_dataset is None:
            return
        code_dataset.ContextIdentifier = VL_DENTAL_VIEW_CID
        code_dataset.ContextGroupExtensionFlag = 'Y'

        # set the version to the current date, as this code is private and could
        # be different for each invocation.
        code_dataset.ContextGroupLocalVersion = datetime.now().strftime(DATE_FORMAT)
        # Determine which Creator UID to use
        if creator_uid is not None:
            code_dataset.ContextGroupExtensionCreatorUID = creator_uid
        elif getattr(code_dataset, 'ContextGroupExtensionCreatorUID', None):
            pass  # already set by caller
        else:
            logger.warning(
                "No ContextGroupExtensionCreatorUID provided by caller or in code_dataset; using dicom4ortho UID. This is probably NOT what you want.")
            code_dataset.ContextGroupExtensionCreatorUID = DICOM4ORTHO_ROOT_UID
        view_seq = getattr(ds, 'ViewCodeSequence', None)
        if not view_seq:
            ds.ViewCodeSequence = Sequence([code_dataset])
            return
        replaced = False
        for idx, item in enumerate(view_seq):
            if (
                getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                getattr(item, 'ContextGroupExtensionFlag', None) == 'Y'
            ):
                view_seq[idx] = code_dataset
                replaced = True
                break
        if not replaced:
            view_seq.append(code_dataset)
        ds.ViewCodeSequence = view_seq

    def _get_code_dataset(self, dent_oip_code_keyword) -> Dataset:
        """ Construct a DICOM Dataset from a row in the codes.csv of DENT_OIP 

        dent_oip_code must be a dictionary with the following keys:
        code
        codeset
        meaning
        """
        dent_oip_code = self.dent_oip.CODES.get(dent_oip_code_keyword)
        if dent_oip_code == None:
            logger.warning(
                "Keyword [%s] did not match any code. Skipping.", dent_oip_code_keyword)
            return None
        code_dataset = Dataset()
        code_dataset.CodeMeaning = dent_oip_code.get(
            'meaning')[:64]  # LO only allows 64 characters
        code_dataset.CodeValue = dent_oip_code.get('code')
        code_dataset.CodingSchemeDesignator = dent_oip_code.get('codeset')
        return code_dataset

    def _get_code_sequence(self, dent_oip_code_keyword) -> Sequence:
        code_dataset = self._get_code_dataset(dent_oip_code_keyword)
        if code_dataset is None:
            return None
        return Sequence([code_dataset])

    def set_dicom_attributes_by_type_keyword(self, type_keyword=None):
        """ Automatically set all DICOM tags, based on the image type keyword in views.csv.

        """
        if type_keyword:
            # Allow for both dash separated and not separated naming
            self.type_keyword = type_keyword.replace('-', '')

        if not self.type_keyword:
            scheduled_protocol_code = self.image_type_code_dataset
            if scheduled_protocol_code is not None and 'CodeValue' in scheduled_protocol_code:
                self.type_keyword = self.image_type_code_dataset.CodeValue

        if not self.type_keyword:
            logger.info("No type_keyword set for %s",
                        self.output_image_filename)
            return

        self.dent_oip_view = self.dent_oip.VIEWS.get(self.type_keyword)
        if self.dent_oip_view is None:
            logger.info("No type_keyword recognized the image type %s for file: %s",
                        self.type_keyword, self.output_image_filename)
            return

        # Get the array of functions to set this required type.
        logger.debug('Setting DICOM attributes for %s', self.type_keyword)

        # Make a nice comment from keyword and description
        ImageComments = f"{self.type_keyword}^{self.dent_oip_view.get('ImageComments')}"

        # NBSP character OxA0 is not allowed in Image Comments. Replace with a
        # Space (0x20)
        self._ds.ImageComments = ImageComments.replace('\xa0', '\x20')

        self._ds.SeriesDescription = self.dent_oip_view.get(
            'SeriesDescription')

        patient_orientation_code = self.dent_oip.CODES.get(
            self.dent_oip_view.get('PatientOrientation'))
        if patient_orientation_code is None:
            patient_orientation_code = self.dent_oip.CODES.get(
                'OrientationFront')
            logger.warning(f"PatientOrientation not found for %s. Defaulting to %s",
                           self.output_image_filename, patient_orientation_code)
        self._ds.PatientOrientation = patient_orientation_code.get(
            'code').split('^')
        self._ds.ImageLaterality = self.dent_oip.CODES.get(
            self.dent_oip_view.get('ImageLaterality')).get('code')

        self.add_device()
        self.add_anatomic_region()
        self.add_view_code()
        self.add_primary_anatomic_structure()
        self.add_acquisition_context()

    def add_acquisition_context(self):
        def add_progress():
            if self.treatment_event_type and self.days_after_event:
                acs_ds = Dataset()
                acs_ds.ValueType = 'CODE'
                acs_ds.ConceptNameCodeSequence = self._get_code_sequence(
                    "TemporalEventType")
                acs_ds.ConceptCodeSequence = self._get_code_sequence(
                    self.treatment_event_type)
                AcquisitionContextSequence.append(acs_ds)

                acs_ds = Dataset()
                acs_ds.ValueType = 'NUMERIC'
                acs_ds.ConceptNameCodeSequence = self._get_code_sequence(
                    "OffsetFromEvent")
                acs_ds.MeasurementUnitsCodeSequence = self._get_code_sequence(
                    "day")
                acs_ds.NumericValue = self.days_after_event
                AcquisitionContextSequence.append(acs_ds)

        AcquisitionContextSequence = Sequence([])
        # Find all columns which start with AcquisitionContextSequence in dent_oip_view
        for index, key in enumerate(self.dent_oip_view):
            if key.startswith("AcquisitionContextSequence"):
                concept_name = key.split("^")[1]
                concept_name_code_sequence = self._get_code_sequence(
                    concept_name)
                for concept_code in self.dent_oip_view.get(key).split("^"):
                    if concept_code != "na" and len(concept_code) > 0:
                        acs_ds = Dataset()
                        acs_ds.ValueType = 'CODE'
                        acs_ds.ConceptNameCodeSequence = concept_name_code_sequence
                        acs_ds.ConceptCodeSequence = self._get_code_sequence(
                            concept_code)
                        AcquisitionContextSequence.append(acs_ds)
        add_progress()
        self._ds.AcquisitionContextSequence = AcquisitionContextSequence

    def add_device(self):
        DeviceSequence = Sequence([])
        for device in self.dent_oip_view.get('DeviceSequence').split("^"):
            if device != "na" and len(device) > 0:
                DeviceSequence.append(self._get_code_dataset(device))
        # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
        if (len(DeviceSequence) > 0):
            self._ds.DeviceSequence = DeviceSequence

    def add_anatomic_region(self):
        # AnatomicRegionSequence allows for a single value
        self._ds.AnatomicRegionSequence = self._get_code_sequence(
            self.dent_oip_view.get('AnatomicRegionSequence'))

        # More than one AnatomicRegionModifierSequence are allowed
        AnatomicRegionModifierSequence = Sequence([])
        for arm in self.dent_oip_view.get('AnatomicRegionModifierSequence').split("^"):
            if arm != "na" and len(arm) > 0:
                AnatomicRegionModifierSequence.append(
                    self._get_code_dataset(arm))
        # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
        if (len(AnatomicRegionModifierSequence) > 0):
            self._ds.AnatomicRegionSequence[0].AnatomicRegionModifierSequence = AnatomicRegionModifierSequence

    def add_view_code(self):
        """ Identical function as add_anatomic_region()
        """
        # ViewCodeSequence allows for a single value
        self._ds.ViewCodeSequence = self._get_code_sequence(
            self.dent_oip_view.get('ViewCodeSequence'))

        # More than one AnatomicRegionModifierSequence are allowed
        ViewModifierCodeSequence = Sequence([])
        for vmcs in self.dent_oip_view.get('ViewModifierCodeSequence').split("^"):
            if vmcs != "na" and len(vmcs) > 0:
                ViewModifierCodeSequence.append(self._get_code_dataset(vmcs))
        # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
        if (len(ViewModifierCodeSequence) > 0):
            self._ds.ViewCodeSequence[0].ViewModifierCodeSequence = ViewModifierCodeSequence

    def add_primary_anatomic_structure(self):
        # PrimaryAnatomicStructureSequence allows for multiple values, but currently only one is supported by this code.
        pas = self.dent_oip_view.get('PrimaryAnatomicStructureSequence')
        if pas != "na" and len(pas) > 0:
            self._ds.PrimaryAnatomicStructureSequence = self._get_code_sequence(
                pas)

            # More than one AnatomicRegionModifierSequence are allowed
            PrimaryAnatomicStructureModifierSequence = Sequence([])
            for pasm in self.dent_oip_view.get('PrimaryAnatomicStructureModifierSequence').split("^"):
                if pasm != "na" and len(pasm) > 0:
                    PrimaryAnatomicStructureModifierSequence.append(
                        self._get_code_dataset(pasm))
            # The AnatomicRegionModifierSequence must be part of AnatomicRegionSequence
            if (len(PrimaryAnatomicStructureModifierSequence) > 0):
                self._ds.PrimaryAnatomicStructureSequence[
                    0].PrimaryAnatomicStructureModifierSequence = PrimaryAnatomicStructureModifierSequence

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
        self.UID = kwargs.get("uid") or generate_dicom_uid(
            root=SeriesInstanceUID_ROOT)
        self.Photos: List[OrthodonticPhotograph] = []

    def __len__(self):
        return len(self.Photos)

    def __iter__(self):
        return iter(self.Photos)

    def add(self, photo: OrthodonticPhotograph) -> None:
        if not isinstance(photo, OrthodonticPhotograph):
            raise TypeError(
                f"'photo' cannot be of type '{type(photo)}'. Can only add objects of type 'OrthodonticPhotograph'")
        self.Photos.append(photo)

    def save(self, filename_prefix=None) -> None:
        logger.info(
            "Requested to save %s Photos within Series %s", len(self.Photos), self.UID)
        i = 0
        for photo in self.Photos:
            i += 1
            photo.series_description = self.description
            photo.series_instance_uid = self.UID
            photo.study_instance_uid = self.StudyUID
            if not photo.output_image_filename:
                photo.output_image_filename = f"{filename_prefix}_{i}.dcm"
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
        self.UID = kwargs.get("uid") or generate_dicom_uid(
            root=StudyInstanceUID_ROOT)
        self.Series = []

    def __len__(self):
        return len(self.Series)

    def __iter__(self):
        return iter(self.Series)

    def add(self, serie: OrthodonticSeries) -> None:
        serie.StudyUID = self.UID
        self.Series.append(serie)

    def save(self) -> None:
        logger.info(
            "Requested to save %s Series within Study %s", len(self.Series), self.UID)
        for serie in self.Series:
            serie.save()
