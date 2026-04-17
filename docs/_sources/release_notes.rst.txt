Release notes
=============

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