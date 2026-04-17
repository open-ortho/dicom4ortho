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
from dicom4ortho.m_dent_oip import OrthoView
from dicom4ortho._generated_codes import CODES, VIEWS

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

        self.type_keyword = ""          # Orthodontic View keyword, e.g. "IV03"
        self._ortho_view: Optional[OrthoView] = None
        self._view_code_keyword: Optional[str] = metadata.get('view_code_keyword')
        self.treatment_event_type = None
        self.days_after_event = None

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

        # Digital Still Camera (DSC): direct image capture
        self._ds.SceneType = 1
        self._ds.FileSource = 3  # Digital Still Camera (DSC)

        # TODO: extract this to a higher level to give the user the ability to set it when needed.
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

    def set_dicom_attributes_by_type_keyword(self, type_keyword=None):
        """Automatically set all DICOM tags based on the image type keyword."""
        if type_keyword:
            # Allow for both dash-separated and non-separated naming
            self.type_keyword = type_keyword.replace('-', '')

        if not self.type_keyword:
            scheduled_protocol_code = self.image_type_code_dataset
            if scheduled_protocol_code is not None and 'CodeValue' in scheduled_protocol_code:
                self.type_keyword = self.image_type_code_dataset.CodeValue

        if not self.type_keyword:
            logger.info("No type_keyword set for %s",
                        self.output_image_filename)
            return

        view = VIEWS.get(self.type_keyword)
        if view is None:
            logger.info("Image type keyword %r not recognised for file: %s",
                        self.type_keyword, self.output_image_filename)
            return

        if view.view_code is None and not self._view_code_keyword:
            raise TypeError(
                f"View {view.keyword!r} requires a 'view_code_keyword' parameter "
                f"(ViewCode is variable for this view — e.g. 'projection_right'). "
                f"Pass it to the constructor or call set_view_code() after construction."
            )

        self._ortho_view = view
        logger.debug('Setting DICOM attributes for %s', self.type_keyword)
        self._apply_view(view)

        if view.view_code is None and self._view_code_keyword:
            self.set_view_code(self._view_code_keyword)

    def _apply_view(self, view: OrthoView) -> None:
        """Set all DICOM tags from a typed OrthoView."""
        # ImageComments (0020,4000)
        comments = f"{view.keyword}^{view.description}"
        self._ds.ImageComments = comments.replace('\xa0', '\x20')

        # SeriesDescription (0008,103E)
        self._ds.SeriesDescription = view.series_description

        # PatientOrientation (0020,0020) — absent when orientation cannot be determined
        if view.patient_orientation is not None:
            self._ds.PatientOrientation = list(view.patient_orientation)

        # ImageLaterality (0020,0062)
        self._ds.ImageLaterality = view.image_laterality

        # DeviceSequence (0050,0010)
        if view.devices:
            self._ds.DeviceSequence = Sequence(
                [c.to_dataset() for c in view.devices])

        # AnatomicRegionSequence (0008,2218)
        ar_ds = view.anatomic_region.to_dataset()
        if view.anatomic_region_modifier is not None:
            ar_ds.AnatomicRegionModifierSequence = Sequence(
                [view.anatomic_region_modifier.to_dataset()])
        self._ds.AnatomicRegionSequence = Sequence([ar_ds])

        # ViewCodeSequence (0054,0220)
        if view.view_code is not None:
            vc_ds = view.view_code.to_dataset()
            if view.view_modifiers:
                vc_ds.ViewModifierCodeSequence = Sequence(
                    [c.to_dataset() for c in view.view_modifiers])
            self._ds.ViewCodeSequence = Sequence([vc_ds])
        # PrimaryAnatomicStructureSequence (0008,2228)
        if view.primary_anatomic_structure is not None:
            pas_ds = view.primary_anatomic_structure.to_dataset()
            if view.primary_anatomic_structure_modifier is not None:
                pas_ds.PrimaryAnatomicStructureModifierSequence = Sequence(
                    [view.primary_anatomic_structure_modifier.to_dataset()])
            self._ds.PrimaryAnatomicStructureSequence = Sequence([pas_ds])

        # AcquisitionContextSequence (0040,0555) — TID 3465
        self._ds.AcquisitionContextSequence = Sequence(
            self._build_acquisition_context_items(view))

    def _build_acquisition_context_items(self, view: OrthoView) -> list:
        """Build TID 3465 AcquisitionContextSequence items from a typed OrthoView."""
        items = []

        def _code_item(concept_name_code, concept_code) -> Dataset:
            ds = Dataset()
            ds.ValueType = 'CODE'
            ds.ConceptNameCodeSequence = concept_name_code.to_sequence()
            ds.ConceptCodeSequence = concept_code.to_sequence()
            return ds

        # TID 3465 row 1: OrthognathicFunctionalCondition (130325, DCM)
        if view.orthognathic_functional_conditions:
            cn = CODES['OrthognathicFunctionalConditions']
            for code in view.orthognathic_functional_conditions:
                items.append(_code_item(cn, code))

        # TID 3465 row 2: FindingByInspection (118243007, SCT)
        if view.findings_by_inspection:
            cn = CODES['FindingByInspection']
            for code in view.findings_by_inspection:
                items.append(_code_item(cn, code))

        # TID 3465 row 3: ObservableEntity (363787002, SCT)
        if view.observable_entities:
            cn = CODES['ObservableEntity']
            for code in view.observable_entities:
                items.append(_code_item(cn, code))

        # TID 3465 row 4: DentalOcclusion (25272006, SCT)
        if view.dental_occlusion is not None:
            items.append(_code_item(CODES['DentalOcclusion'], view.dental_occlusion))

        # TID 3465 rows 5-6: Treatment progress (set by library user)
        items.extend(self._make_progress_items())

        return items

    def _make_progress_items(self) -> list:
        """Build TID 3465 rows 5-6 from treatment_event_type and days_after_event."""
        if not (self.treatment_event_type and self.days_after_event is not None):
            return []

        event_code = CODES.get(self.treatment_event_type)
        if event_code is None:
            logger.warning(
                "treatment_event_type %r not found in codes; skipping progress items.",
                self.treatment_event_type)
            return []

        items = []

        # Row 5: Longitudinal Temporal Event Type
        event_ds = Dataset()
        event_ds.ValueType = 'CODE'
        event_ds.ConceptNameCodeSequence = CODES['TemporalEventType'].to_sequence()
        event_ds.ConceptCodeSequence = event_code.to_sequence()
        items.append(event_ds)

        # Row 6: Longitudinal Temporal Offset from Event
        offset_ds = Dataset()
        offset_ds.ValueType = 'NUMERIC'
        offset_ds.ConceptNameCodeSequence = CODES['OffsetFromEvent'].to_sequence()
        offset_ds.MeasurementUnitsCodeSequence = CODES['day'].to_sequence()
        offset_ds.NumericValue = self.days_after_event
        items.append(offset_ds)

        return items

    def set_view_code(self, keyword: str) -> None:
        """Set (or replace) ViewCodeSequence, attaching any view modifiers defined
        for this view.

        Required for incomplete views (e.g. IV28, IV30, EV40) whose ViewCode is
        variable and must be supplied by the caller.  May also be called after
        construction to change the ViewCode.

        :param keyword: keyword from codes.csv (e.g. 'projection_right')
        """
        code = CODES.get(keyword)
        if code is None:
            logger.warning(
                "view_code_keyword %r not found in codes; ViewCodeSequence not set.",
                keyword)
            return
        vc_ds = code.to_dataset()
        if self._ortho_view and self._ortho_view.view_modifiers:
            vc_ds.ViewModifierCodeSequence = Sequence(
                [c.to_dataset() for c in self._ortho_view.view_modifiers])
        self._ds.ViewCodeSequence = Sequence([vc_ds])

    def set_treatment_progress(self, event_type: str, days: int) -> None:
        """Set the longitudinal temporal event type and offset (TID 3465 rows 5-6).

        Updates AcquisitionContextSequence in place, rebuilding it from the
        current view plus the new progress values.

        :param event_type: keyword from codes.csv (e.g. 'OrthodonticTreatment')
        :param days: number of days after the event
        """
        self.treatment_event_type = event_type
        self.days_after_event = days
        if self._ortho_view is not None:
            self._ds.AcquisitionContextSequence = Sequence(
                self._build_acquisition_context_items(self._ortho_view))
        else:
            # No view set; just write the progress items on their own
            self._ds.AcquisitionContextSequence = Sequence(
                self._make_progress_items())

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
