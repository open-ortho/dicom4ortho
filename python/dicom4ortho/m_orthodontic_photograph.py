# pylint: disable=invalid-name
''' Orthodontic Photograph Classes.

Adds SNOMED CT codes in DICOM object for Orthodontic Views.

'''

from typing import List, Optional
from copy import deepcopy
from datetime import date, datetime
import warnings
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset
from dicom4ortho.config import VL_DENTAL_VIEW_CID, DATE_FORMAT

from dicom4ortho.model import PhotographBase
from dicom4ortho.config import IMPORT_DATE_FORMAT, SeriesInstanceUID_ROOT, StudyInstanceUID_ROOT
from dicom4ortho.utils import generate_dicom_uid
from dicom4ortho.m_dent_oip import OrthoView
from dicom4ortho._generated_codes import CODES, VIEWS, IMAGE_TYPES
from dicom4ortho.photograph_protocols import requested_view_codes, set_view_code

import logging
logger = logging.getLogger(__name__)


TREATMENT_EVENT_TYPES = frozenset({
    'PatientRegistration',
    'OrthodonticTreatmentStarted',
    'OrthodonticTreatmentStopped',
})

# TODO(v2): Remove these aliases when support for deprecated APIs is removed in version >= 2.
_DEPRECATED_TREATMENT_EVENT_ALIASES = {
    'OrthodonticTreatment': 'OrthodonticTreatmentStarted',
    'Posttreatment': 'OrthodonticTreatmentStopped',
}


class OrthodonticPhotograph(PhotographBase):
    """ An Orthodontic Photograph as defined in WP-1100

        EXIF ``DateTimeOriginal`` is used as the acquisition time when present.
        Passing ``acquisition_datetime`` overrides EXIF and supplies the date
        used to calculate treatment progress.

        ``dental_provider_firstname`` and ``dental_provider_lastname`` identify
        the orthodontist or dentist responsible for treatment and are encoded
        as DICOM Physicians of Record. ``operator_firstname`` and
        ``operator_lastname`` identify the clinical staff member who acquired
        the photographs and are encoded as DICOM Operators' Name.

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
        self.treatment_event_date = None
        self.days_after_event = None

        # PhotographBase has already loaded EXIF as fallback metadata. An
        # explicit value intentionally overrides it before progress is calculated.
        acquisition_datetime = self._optional_metadata(metadata, 'acquisition_datetime')
        if acquisition_datetime is not None:
            self.set_time_captured(self._coerce_datetime(acquisition_datetime))

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
        dental_provider_firstname = metadata.get('dental_provider_firstname')
        dental_provider_lastname = metadata.get('dental_provider_lastname')
        if dental_provider_firstname:
            self.dental_provider_firstname = dental_provider_firstname
        if dental_provider_lastname:
            self.dental_provider_lastname = dental_provider_lastname

        operator_firstname = metadata.get('operator_firstname')
        operator_lastname = metadata.get('operator_lastname')
        if operator_firstname:
            self.operator_firstname = operator_firstname
        if operator_lastname:
            self.operator_lastname = operator_lastname
        self.equipment_manufacturer = metadata.get('manufacturer')
        event_type = self._optional_metadata(metadata, 'treatment_event_type')
        event_date = self._optional_metadata(metadata, 'treatment_event_date')
        days_after_event = self._optional_metadata(metadata, 'days_after_event')
        if event_date is not None and days_after_event is not None:
            raise ValueError(
                "Specify either treatment_event_date or days_after_event, not both.")
        if event_type is None and (event_date is not None or days_after_event is not None):
            raise ValueError(
                "treatment_event_type is required with treatment progress metadata.")
        if event_type is not None and event_date is None and days_after_event is None:
            raise ValueError(
                "treatment_event_date or days_after_event is required with "
                "treatment_event_type.")
        if event_type is not None:
            self.treatment_event_type = self._canonical_treatment_event(event_type)
        if event_date is not None:
            self.treatment_event_date = self._coerce_date(event_date)
            self.days_after_event = self._days_since_event(self.treatment_event_date)
        elif days_after_event is not None:
            # TODO(v2): Remove days_after_event metadata support in version >= 2.
            warnings.warn(
                "days_after_event is deprecated; use treatment_event_date with "
                "acquisition_datetime instead. Support will be removed in version 2.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.days_after_event = self._validate_days(days_after_event)

        if self.treatment_event_type is not None:
            self._set_treatment_progress(self.treatment_event_type, self.days_after_event)

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

        Read RequestAttributesSequence.ScheduledProtocolCodeSequence (DENT-OIP #12).
        Return a code only when exactly one qualifying occurrence exists; a series
        prescription with several views does not uniquely identify this instance.
        Legacy private ViewCodeSequence is a read-only fallback.
        """
        codes = requested_view_codes(ds)
        if not codes:
            codes = [item for item in getattr(ds, 'ViewCodeSequence', [])
                     if getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID
                     and getattr(item, 'ContextGroupExtensionFlag', None) == 'Y']
        if len(codes) == 1:
            return codes[0]
        if codes:
            logger.warning('Multiple view prescriptions; no unique instance type can be selected.')
        return None

    @staticmethod
    def set_image_type_code_dataset(ds: Dataset, code_dataset: Dataset, creator_uid: str = None,
                                    *, request_index: int | None = None,
                                    protocol_index: int | None = None) -> None:
        """
        Set the code that defines this image type.

        Write RequestAttributesSequence.ScheduledProtocolCodeSequence, not
        ViewCodeSequence. Preserve request context and unrelated codes. Select
        explicit indices for multi-request/multi-view lists; do not guess an
        instance association from InstanceNumber. No CID 4063 extension is added:
        that context describes projections, not scheduled photograph protocols.

        This function modifies the given Dataset in place and does not return a value.

        See DENT-OIP #12 and section 3.4.1.3. The historical creator_uid argument
        is accepted only for an explicitly declared, fully supplied extension
        context. A creator UID without extension flag Y is invalid, including when
        it is embedded in code_dataset. Invalid input raises before ds is changed.

        :param ds: The DICOM Dataset to modify
        :param code_dataset: The code Dataset to insert/update
        :param creator_uid: Optional creator for a supplied extension context; no default is invented.
        """
        if code_dataset is None:
            return
        code_dataset = deepcopy(code_dataset)
        if creator_uid is not None:
            code_dataset.ContextGroupExtensionCreatorUID = creator_uid
        if getattr(code_dataset, 'ContextGroupExtensionCreatorUID', None) is not None:
            if getattr(code_dataset, 'ContextGroupExtensionFlag', None) != 'Y':
                raise ValueError('ContextGroupExtensionCreatorUID requires extension flag Y.')
        if getattr(code_dataset, 'ContextGroupExtensionFlag', None) == 'Y':
            required = ('ContextIdentifier', 'MappingResource', 'ContextGroupVersion',
                        'ContextGroupLocalVersion', 'ContextGroupExtensionCreatorUID')
            if any(not getattr(code_dataset, keyword, None) for keyword in required):
                raise ValueError('A private extension requires its complete supplied context.')
        set_view_code(ds, code_dataset, request_index=request_index, protocol_index=protocol_index)

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

        # IV29 retains known anatomy without inventing a direction while the
        # profile decision is pending: open-ortho/dent-oip#63.
        if (view.view_code is None and not self._view_code_keyword
                and view.keyword != 'IV29'):
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
        # A supplied worklist/series protocol list is authoritative request context.
        # Do not replace it with this instance's view or append an unscheduled view.
        if not any(getattr(request, 'ScheduledProtocolCodeSequence', [])
                   for request in getattr(self._ds, 'RequestAttributesSequence', [])):
            self.set_image_type_code_dataset(self._ds, IMAGE_TYPES[view.keyword].code.to_dataset())
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
        elif 'ViewCodeSequence' in self._ds:
            # A previous image type does not establish this photograph's direction.
            del self._ds.ViewCodeSequence
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

        event_code = CODES[self.treatment_event_type]

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

        Required for incomplete views (IV28, IV30, EV40) whose ViewCode is
        variable and must be supplied by the caller. Optional for IV29, whose
        unknown direction is omitted. May also be called after construction to
        change the ViewCode.

        :param keyword: generated terminology keyword (e.g. 'projection_right')
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

    @staticmethod
    def _optional_metadata(metadata: dict, keyword: str):
        """Return None for omitted or blank optional metadata values."""
        value = metadata.get(keyword)
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @staticmethod
    def _canonical_treatment_event(event_type: str) -> str:
        """Validate an event type and return its canonical CID 4070 keyword."""
        canonical_event = _DEPRECATED_TREATMENT_EVENT_ALIASES.get(event_type)
        if canonical_event is not None:
            warnings.warn(
                f"{event_type!r} is deprecated; use {canonical_event!r}. "
                "Support will be removed in version 2.",
                DeprecationWarning,
                stacklevel=3,
            )
            return canonical_event
        if event_type not in TREATMENT_EVENT_TYPES:
            allowed = ', '.join(sorted(TREATMENT_EVENT_TYPES))
            raise ValueError(
                f"Unknown treatment event type {event_type!r}; expected one of {allowed}.")
        return event_type

    @staticmethod
    def _validate_days(days: int) -> int:
        """Return a non-negative integer day offset."""
        if isinstance(days, bool):
            raise TypeError("days must be a non-negative integer.")
        try:
            validated_days = int(days)
        except (TypeError, ValueError) as error:
            raise TypeError("days must be a non-negative integer.") from error
        if str(validated_days) != str(days).strip() or validated_days < 0:
            raise ValueError("days must be a non-negative integer.")
        return validated_days

    @staticmethod
    def _coerce_date(value) -> date:
        """Return a date from a date, datetime, or ISO date string."""
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as error:
                raise ValueError(
                    f"Expected an ISO date (YYYY-MM-DD), got {value!r}.") from error
        raise TypeError("event and acquisition dates must be date values or ISO date strings.")

    @staticmethod
    def _coerce_datetime(value) -> datetime:
        """Return a datetime from a datetime or ISO datetime string."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError as error:
                raise ValueError(
                    f"Expected an ISO datetime, got {value!r}.") from error
        raise TypeError("acquisition_datetime must be a datetime or ISO datetime string.")

    def _acquisition_date(self) -> date:
        value = getattr(self._ds, 'AcquisitionDate', None)
        if value:
            return datetime.strptime(str(value), DATE_FORMAT).date()
        raise ValueError(
            "An acquisition date is required to calculate treatment progress.")

    def _days_since_event(self, event_date: date, acquisition_date=None) -> int:
        acquired = (
            self._coerce_date(acquisition_date)
            if acquisition_date is not None
            else self._acquisition_date()
        )
        days = (acquired - event_date).days
        if days < 0:
            raise ValueError("treatment_event_date cannot be after the acquisition date.")
        return days

    def _set_treatment_progress(self, event_type: str, days: int) -> None:
        """Store canonical progress values and rebuild AcquisitionContextSequence."""
        self.treatment_event_type = event_type
        self.days_after_event = days
        if self._ortho_view is not None:
            self._ds.AcquisitionContextSequence = Sequence(
                self._build_acquisition_context_items(self._ortho_view))
        else:
            self._ds.AcquisitionContextSequence = Sequence(
                self._make_progress_items())

    def set_treatment_progress(self, event_type: str, days: int) -> None:
        """Set treatment progress from a caller-calculated day offset.

        .. deprecated:: 0.5.3
           Use :meth:`set_treatment_progress_from_date` so dicom4ortho calculates
           and validates the offset.

        Updates AcquisitionContextSequence in place, rebuilding it from the
        current view plus the new progress values.

        :param event_type: canonical CID 4070 keyword
        :param days: number of days after the event
        """
        # TODO(v2): Remove this days-based method in version >= 2.
        warnings.warn(
            "set_treatment_progress(event_type, days) is deprecated; use "
            "set_treatment_progress_from_date(). Support will be removed in version 2.",
            DeprecationWarning,
            stacklevel=2,
        )
        canonical_event = self._canonical_treatment_event(event_type)
        self.treatment_event_date = None
        self._set_treatment_progress(canonical_event, self._validate_days(days))

    def set_treatment_progress_from_date(
        self, event_type: str, event_date, acquisition_date=None
    ) -> None:
        """Set treatment progress from an event date and photograph date.

        If ``acquisition_date`` is omitted, Acquisition Date is read from the
        DICOM dataset. Content Date is not a capture-time source. Only the
        calculated day offset is encoded, as required by TID 3465.

        :param event_type: PatientRegistration, OrthodonticTreatmentStarted,
                           or OrthodonticTreatmentStopped
        :param event_date: event date as a date, datetime, or ISO date string
        :param acquisition_date: optional photograph date override
        """
        canonical_event = self._canonical_treatment_event(event_type)
        validated_event_date = self._coerce_date(event_date)
        days = self._days_since_event(validated_event_date, acquisition_date)
        self.treatment_event_date = validated_event_date
        self._set_treatment_progress(canonical_event, days)

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
