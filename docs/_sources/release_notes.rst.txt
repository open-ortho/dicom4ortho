Release notes
=============

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
* Load views and codes from ADA-1107
* Fix Patient, Doctor and Operator names
* Add support for JPEG2000
* UID is now generated from hashing the input file
* Other bug fixes