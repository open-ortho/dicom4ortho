Release notes
=============

0.5.3
-----

* **Authoritative terminology**: DICOM codes are resolved directly from NEMA
  FHIR ValueSets and DCM concept names from NEMA ``dcm.owl``, not the previously
  proposed pinned ``fhir.dicom`` package. All 73 ADA 1100 image types are resolved
  from the CodeSystems at ``terminology.open-ortho.org``.
* **Offline terminology lock**: ``SOURCE_PROVENANCE`` in the committed
  ``dicom4ortho/_generated_codes.py`` records observed source URLs, SHA-256s,
  and available FHIR version/date metadata. Normal builds and runtime do not
  access the network.
* **Retired terminology CSV files**: ``codes.csv`` and ``image_types.csv`` are
  no longer packaged. Regeneration downloads ``views.csv`` directly from the
  ANSI/ADA-1107 source repository; the packaged copy is only a compatibility/test
  snapshot.
* **Correct CID 4070 events**: treatment progress now uses
  ``PatientRegistration`` (``184047000``), ``OrthodonticTreatmentStarted``
  (``1332161000``), and ``OrthodonticTreatmentStopped`` (``1340210007``).
* **Date-based treatment progress**:
  ``set_treatment_progress_from_date(event_type, event_date)`` calculates the
  TID 3465 offset from the photograph acquisition date. Constructor metadata
  accepts ``treatment_event_date`` with ``acquisition_datetime``.
* **Acquisition-time precedence**: an explicit ``acquisition_datetime``
  overrides EXIF. If it is omitted, EXIF ``DateTimeOriginal`` is loaded before
  treatment progress is calculated and used as the fallback acquisition time.
  Editing/digitization timestamps are not acquisition-time sources. Supplied
  progress is encoded even when no image type is resolved.
* **Compatibility**: the days-based API and the old ``OrthodonticTreatment``
  and ``Posttreatment`` event names remain available with
  ``DeprecationWarning`` until version 2.
* **Resource maintenance**: ``make update_codes`` explicitly downloads all
  terminology sources and the view layout, then regenerates the lock without
  committing it. ``make check_codes`` performs the same fetch/validation in
  memory and fails on drift without rewriting the file. These replace the
  removed ``make update_resources`` command; ``make fetch_resources`` only
  updates the packaged CSV snapshot and is not required for regeneration.
* **Coding changes**: the mirror device now uses SCT ``1332162007`` (intraoral
  photography mirror), replacing ``47162009``. This is a code change, not only
  a display-text update. SCT ``7652006`` uses the current CID 4061 meaning
  ``Frenulum labii`` without a local display override.
* **IV29 direction**: frenum photographs no longer assume a frontal projection.
  An unknown direction and its nested close-up modifier are omitted while
  retaining mouth/frenum anatomy. A direction can be supplied at construction
  or later. This is interim behavior pending the profile decision in
  `ANSI/ADA-1107 issue 63 <https://github.com/open-ortho/dent-oip/issues/63>`_.
* **Practice personnel**: ``dental_provider_firstname`` and
  ``dental_provider_lastname`` now encode the orthodontist or dentist
  responsible for treatment as DICOM Physicians of Record. Explicit operator
  metadata encodes the clinical staff member as Operators' Name, while an
  actual referring physician is copied from MWL without conflating it with the
  requesting physician.
* **MWL conversion**: the controller's image-plus-worklist conversion now copies
  valid worklist attributes and returns the generated photograph.
* **JPEG 2000 preserved as received**: the source codestream is encapsulated
  unchanged instead of being decoded and re-encoded, and the Transfer Syntax and
  ``LossyImageCompression`` follow its wavelet transform. A JP2 container is
  unwrapped to its ``jp2c`` codestream first.

0.5.2
-----

* **CP-1570 / TID 3465 compliance**: ``OrthodonticPhotograph`` now builds
  ``AcquisitionContextSequence`` from typed ``OrthoView`` fields mapping
  directly to TID 3465 rows (OrthognathicFunctionalCondition, FindingByInspection,
  ObservableEntity, DentalOcclusion, and optional LongitudinalTemporalEventType +
  Offset via ``set_treatment_progress()``).
* **Build-time code generation**: replaced runtime CSV parsing with a
  code-generation pipeline (``tools/generate_codes.py``). Reads ``codes.csv``
  and ``views.csv`` and emits ``dicom4ortho/_generated_codes.py`` — a committed
  lock file of typed Python constants (``DicomCode``, ``OrthoView``). No network
  I/O at runtime.
* **Typed data layer**: two new frozen dataclasses in ``m_dent_oip.py`` —
  ``DicomCode`` (with ``to_dataset()`` / ``to_sequence()``) and ``OrthoView``
  (all 73 view definitions with typed fields for every DICOM attribute).
* **Incomplete-view enforcement**: views with a variable ``ViewCodeSequence``
  (IV28, IV30, EV40) now raise ``TypeError`` immediately at construction unless
  ``view_code_keyword`` is supplied. ``set_view_code()`` fills the slot and
  auto-attaches any predefined ``ViewModifierCodeSequence``.
* **codes.csv / views.csv corrections**: ``OrthognathicFunctionalConditions``
  concept-name code corrected (``ZZZZZZ`` → ``130325``, DCM, per CP-1570);
  ``closeup`` keyword mismatch fixed; IV29 given ``projection_frontal`` as its
  fixed ViewCode.
* **CLI fix**: ``dicom4ortho list-image-types`` now works correctly (fixed
  ``TypeError: 'PosixPath' object is not iterable`` in ``print_image_types()``);
  help text updated to show the full command.
* **CLI cleanup**: removed ``--url-codes`` / ``--url-views`` flags (broken since
  the refactor; resource updates are now a build-time operation via
  ``make update_resources``).
* **Dev environment**: ``flake.nix`` rewritten to use pip/pyproject.toml as the
  single source of truth for Python deps; ``dciodvfy`` and ``dcmtk`` added to
  the Nix shell.
* **Makefile**: ``make update_resources`` now only regenerates
  ``_generated_codes.py`` from committed CSVs; new ``make fetch_resources``
  target does the upstream curl downloads separately. New ``make help`` default
  target.
* **Tests**: 29 new tests in ``test/test_generated_codes.py`` covering CSV
  consistency, all 73 view attribute correctness, and the ``view_code_keyword``
  / ``set_view_code()`` API.

0.5.1
-----

* Rename ``get/set_image_type_code_sequence`` → ``get/set_image_type_code_dataset``
  for consistency with pydicom naming conventions.
* Add tests for image type code dataset handling in ``OrthodonticPhotograph``.
* Refactor test files for improved organisation and logging consistency.

0.4.7
-----

* Fix default Series and Study Date and Time to empty.

0.4.2
-----

* Add partial support for EXIF metadata: copy tags from EXIF to DICOM according to standard. Only Manufacturer related and date related tags are copied.

0.4
---

* Add support for DICOM MWL (Modality Worklist): copy tags from MWL
* Add support for using InstanceNumber and ScheduledProtocolCode to define image type
* Add method to decode the image type from the InstanceNumber and ScheduledProtocolCodeSequence
* Remove code related to teeth
* Add setters for Series and Instance Numbers

0.2
---

* Add BurnedInAnnotation, Operator, Institution and Performing Physician tags
* Load views and codes from ANSI/ADA-1107
* Fix Patient, Doctor and Operator names
* Add support for JPEG2000
* UID is now generated from hashing the input file
* Other bug fixes
