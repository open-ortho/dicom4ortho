Usage
=====

The DICOM images require a lot of information which is not contained in
a flat PNG or JPEG image. This information would, in a production
environment, usually come from the practice management software, or
photo management software.

CLI
----

The CLI accepts either a single image or a CSV file for bulk conversion. List
the supported ADA 1100 image types with:

.. code-block:: bash

   dicom4ortho list-image-types

Once installed, use dicom4ortho like this:

.. code-block:: bash

   dicom4ortho --image-type EV08 input.jpg

For bulk conversion, pass a CSV file using the format described in
:doc:`file_formats/csv_file`. The source repository includes a tested,
executable `CSV example <https://github.com/open-ortho/dicom4ortho/blob/develop/examples/input_from.csv>`__
with its referenced images in the same directory.

Using the library directly
---------------------------

Create an orthodontic photograph directly by passing an ADA 1100 image type
and the available metadata:

.. code-block:: python

   from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph

   photo = OrthodonticPhotograph(
       image_type="EV08",
       input_image_filename="input.jpg",
       output_image_filename="output.dcm",
       patient_id="12345",
   )
   photo.save()

Practice personnel
------------------

Keep personnel metadata simple and describe the role each person actually had:

* ``dental_provider_firstname`` and ``dental_provider_lastname`` identify the
  orthodontist or dentist responsible for treatment. They are encoded as DICOM
  Physicians of Record (0008,1048).
* ``operator_firstname`` and ``operator_lastname`` identify the clinical staff
  member who acquired the photographs. They are encoded as DICOM Operators'
  Name (0008,1070).

.. note::

   DICOM permits multiple Physicians of Record and Operators (value
   multiplicity ``1-n``). The current ``dicom4ortho`` public metadata API
   supports one dental provider and one operator per photograph. Multiple
   names are not currently supported.

An actual referring physician is copied from ``ReferringPhysicianName`` in a
Modality Worklist. The requesting physician remains part of the worklist order
and is linked through the request identifiers rather than copied into the
baseline VL Photographic Image IOD.

Orthodontic treatment progress
------------------------------

Treatment progress is encoded as one TID 3465 event and day-offset pair. Use
the event that applies when the photograph was acquired:

* ``PatientRegistration`` before treatment and during observation.
* ``OrthodonticTreatmentStarted`` during active treatment.
* ``OrthodonticTreatmentStopped`` after treatment.

Pass the event date and acquisition datetime so ``dicom4ortho`` calculates and
validates the offset:

.. code-block:: python

   from datetime import date, datetime

   from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph

   photo = OrthodonticPhotograph(
       image_type="EV08",
       acquisition_datetime=datetime(2026, 7, 14, 10, 30),
       treatment_event_type="PatientRegistration",
       treatment_event_date=date(2026, 7, 1),
   )

``acquisition_datetime`` is authoritative when supplied and overrides the
image's EXIF ``DateTimeOriginal`` value. If it is omitted, ``dicom4ortho`` uses
EXIF as the acquisition time and as the basis for calculating treatment
progress. Date-based progress requires one of these acquisition-time sources.

For an existing photograph whose dataset contains an acquisition date, use:

.. code-block:: python

   photo.set_treatment_progress_from_date(
       "OrthodonticTreatmentStarted", date(2026, 7, 1)
   )

An event date after the effective acquisition date is rejected. The event type
and event date must be supplied together.

The old ``days_after_event`` metadata and
``set_treatment_progress(event_type, days)`` method remain available with
``DeprecationWarning`` until version 2. The old ``OrthodonticTreatment`` and
``Posttreatment`` names map to ``OrthodonticTreatmentStarted`` and
``OrthodonticTreatmentStopped`` respectively and are deprecated on the same
schedule.

Updating terminology codes
--------------------------

Terminology updates are an explicit maintainer operation. See
:doc:`terminology` for the authoritative FHIR sources, offline lock behavior,
and update commands.
