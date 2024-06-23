.. _specifications:

dicom4ortho Specifications
==========================

Specifications of how the software should behave and expectations of what it should do. Goals for development.


In general, the main goal of ``dicom4ortho`` is to provide an example for the acquisition and exchange of orthodontic photographs making use of DICOM and other open standards, such as HL7 and SNOMED.

Compliance
-----------

- **CO-01** ``dicom4ortho`` SHALL comply to all specifications and requirements defined in ADA-1107.
- **CO-02** ``dicom4ortho`` SHALL support each view covered in ADA-1107.
- **CO-03** ``dicom4ortho`` SHALL support each viewset covered in ADA-1107.

IF Image Formats
------------------

- **IF-01:** ``dicom4ortho`` SHALL support importing images in the JPEG format. This is because most camera used by orthodontists save the images in this format.
- **IF-02:** ``dicom4ortho`` SHALL support importing images in the JPEG-2000 format. This is because this would be the preferred image format, and can be encapsulated in DICOM.
- **IF-03:** ``dicom4ortho`` SHALL support exporting images in DICOM format as JPEGLossless.
- **IF-04:** ``dicom4ortho`` SHALL support exporting images in DICOM format as JPEG-2000.


II Image Importing
------------------

- **II-01:** ``dicom4ortho`` SHALL read images via FHIR 
   
IE Image Exporting
------------------

- **IE-01:** ``dicom4ortho`` SHALL export images exclusively and only utilizing a well established medical enterprise imaging format such as DICOM.
- **IE-02:** ``dicom4ortho`` SHALL support exporting images to file.
- **IE-03:** ``dicom4ortho`` SHALL support sending images to a DICOM node (as SCU or SCP, DICOMweb, WADO, or whatever).
 
MR Metadata Retrieval
---------------------

- **MR-01:** ``dicom4ortho`` SHALL be able to automatically retrieve clinical metadata in order to create complete DICOM images in accordance to well established standards, such as ADA 1107.
- **MR-02:** ``dicom4ortho`` SHALL support retrieving metadata via FHIR Resources.
- **MR-03:** ``dicom4ortho`` COULD support retrieving metadata via DICOM Modality Worklists (MWL).

SE Security
-----------

It is outside of the scope of ``dicom4ortho`` to deal with security issues. These should be dealt with other tools.

- **SE-01:** ``dicom4ortho`` SHOULD not provide any type of security or log in mechanism.