CSV Image file format
~~~~~~~~~~~~~~~~~~~~~

This is the documentation for the CSV file format used for bulk processing, not the one used to decide which attributes for which view.

A tested, executable `example CSV <https://github.com/open-ortho/dicom4ortho/blob/develop/examples/input_from.csv>`__
is maintained with its referenced images in the source repository. The CLI
test executes this public example to prevent documentation drift.

The CSV file should be:

-  with ``,`` as separator
-  ``UTF-8`` encoded

Each CSV file should containt the following columns (header)

patient_firstname
^^^^^^^^^^^^^^^^^

Patient first name. First part of DICOM tag
``(0010, 0010) Patient's Name``.

patient_lastname
^^^^^^^^^^^^^^^^

Patient last name. Second part of DICOM tag
``(0010, 0010) Patient's Name``.

patient_id
^^^^^^^^^^

Patient ID. DICOM ``(0010, 0020) Patient ID`` tag.

patient_sex
^^^^^^^^^^^

Patient’s gender. DICOM ``(0010, 0040) Patient's Sex`` tag.

patient_birthdate
^^^^^^^^^^^^^^^^^

Patient’s date of birth in YYYY-MM-DD format. DICOM
``(0010, 0030) Patient's Birth Date`` tag.

dental_provider_firstname
^^^^^^^^^^^^^^^^^^^^^^^^^

First name of orthodontic (or dental) provider. First part of DICOM
``(0008, 0090) Referring Physician's Name`` tag.

dental_provider_lastname
^^^^^^^^^^^^^^^^^^^^^^^^

Last name of orthodontic (or dental) provider. Second part of DICOM
``(0008, 0090) Referring Physician's Name`` tag.

image_type
^^^^^^^^^^

Image type as defined by ADA SCDI WP-1100. Type

::

   dicom4ortho list-image-types

for a list of allowed image types.

manufacturer
^^^^^^^^^^^^

Manufacturer of Camera. For example, when using an iPhone, use ``Apple``
here. Overrides input file’s EXIF metadata.

input_image_filename
^^^^^^^^^^^^^^^^^^^^

Full path of flat JPG/PNG/TIFF image file to use as input.

study_instance_uid
^^^^^^^^^^^^^^^^^^

The unique identifier that distinguishes this study from any other
study. For orthodontic purposes, all images taken during the same
patient visit, should go under the same study, thus have the same study
UID.

This is a DICOM UID object and goes into the DICOM
``(0020, 000d) Study Instance UID`` tag. The exact format is defined in
`DICOM Part 5 Data Structures and Encoding - Value Encoding - Value
Representation <http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2>`__

study_description
^^^^^^^^^^^^^^^^^

A description for this specific study. For orthodontic purposes, this
value could be something like ‘Initial Visit’.

This is a DICOM UID object and goes into the DICOM
``(0008, 1030) Study Description``. Maximum 64 characters are allowed,
as defined the `DICOM LO
VR <http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2>`__

series_instance_uid
^^^^^^^^^^^^^^^^^^^

The unique identifier that distinguishes this series from any other
series. For orthodontic purposes, all images taken with the same imaging
device (for photographs, this would be the camera) and during the same
study (hence appointment visit) should be part of the same series, thus
have the same series UID.

This is a DICOM UID object and goest into the DICOM
``(0020, 000e) Series Instance UID`` tag. The exact format is defined in
`DICOM Part 5 Data Structures and Encoding - Value Encoding - Value
Representation <http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2>`__

series_description
^^^^^^^^^^^^^^^^^^

A description for this specific series. For orthodontic purposes, this
value could be something like ‘Orthodontic Intraoral Series’.

This is a DICOM UID object and goes into the DICOM
``(0008, 103e) Series Description``. Maximum 64 characters are allowed,
as defined the `DICOM LO
VR <http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2>`__

Optional treatment-progress columns
-----------------------------------

Blank optional values are ignored. When treatment progress is supplied, the
event type and one offset source must be provided together.

acquisition_datetime
^^^^^^^^^^^^^^^^^^^^

The photograph acquisition date and time as an ISO 8601 value, for example
``2026-07-14T10:30:00``. It is written to the DICOM acquisition and content
date/time attributes and is used to calculate the treatment-progress offset.
When supplied, it overrides EXIF ``DateTimeOriginal``. When omitted,
``dicom4ortho`` uses the EXIF timestamp if one is available.

treatment_event_type
^^^^^^^^^^^^^^^^^^^^

The applicable CID 4070 event. Allowed values are
``PatientRegistration``, ``OrthodonticTreatmentStarted``, and
``OrthodonticTreatmentStopped``.

treatment_event_date
^^^^^^^^^^^^^^^^^^^^

The event date in ``YYYY-MM-DD`` format. ``dicom4ortho`` subtracts this date
from the effective acquisition date, whether explicit or from EXIF, and writes
the resulting non-negative day offset to TID 3465. An event date after the
acquisition date is rejected.

days_after_event
^^^^^^^^^^^^^^^^

A caller-calculated non-negative day offset. This field is retained for
compatibility but is deprecated; use ``treatment_event_date`` with
``acquisition_datetime`` instead. Do not provide both offset forms.

Other optional columns
----------------------

output_image_filename
^^^^^^^^^^^^^^^^^^^^^

The destination DICOM filename. If omitted, the input filename is used with a
``.dcm`` extension.

burned_in_annotation
^^^^^^^^^^^^^^^^^^^^

Set DICOM ``BurnedInAnnotation`` to ``YES`` or ``NO``. The default is ``NO``.

view_code_keyword
^^^^^^^^^^^^^^^^^

The generated terminology keyword for a view code that cannot be determined
from the image type alone. This is required for variable-view image types such
as IV28, IV30, and EV40.
