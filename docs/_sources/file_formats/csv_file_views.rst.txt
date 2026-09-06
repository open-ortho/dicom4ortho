.. _csv_file_views:

View-layout CSV file
====================

Introduction
------------

``dicom4ortho/resources/views.csv`` is a maintainer resource that defines the
DICOM attribute layout for each of the 73 ADA 1100 image types. It is not the
bulk-conversion input format used by the CLI.

Cells that name coded concepts contain generator binding keywords. During an
explicit terminology update, ``tools/generate_codes.py`` resolves those
keywords against the official sources described in :doc:`../terminology`.
There is no separate local codes table.

File structure
--------------

.. list-table:: CSV header descriptions
   :widths: 50 50
   :header-rows: 1

   * - Header
     - Description
   * - keyword
     - The ADA 1100 image-type code for this view.
   * - PatientOrientation
     - A structural orientation keyword resolved by the generator.
   * - ImageLaterality
     - A structural laterality keyword resolved by the generator.
   * - AnatomicRegionSequence
     - A terminology binding for ``AnatomicRegionSequence``.
   * - AnatomicRegionModifierSequence
     - An optional terminology binding for ``AnatomicRegionModifierSequence``.
   * - PrimaryAnatomicStructureSequence
     - An optional terminology binding for ``PrimaryAnatomicStructureSequence``.
   * - PrimaryAnatomicStructureModifierSequence
     - An optional terminology binding for the primary structure modifier.
   * - DeviceSequence
     - Zero or more device bindings separated by ``^``.
   * - ViewCodeSequence
     - A view-code binding. Some views require the caller to supply this value.
   * - ViewModifierCodeSequence
     - Zero or more view-modifier bindings separated by ``^``.
   * - AcquisitionContextSequence^OrthognathicFunctionalConditions
     - Zero or more CID 4066 bindings separated by ``^``.
   * - AcquisitionContextSequence^FindingByInspection
     - Zero or more CID 4067 bindings separated by ``^``.
   * - AcquisitionContextSequence^ObservableEntity
     - Zero or more CID 4068 bindings separated by ``^``.
   * - AcquisitionContextSequence^DentalOcclusion
     - An optional CID 4069 binding.
   * - ImageComments
     - Legacy source data. Runtime ``ImageComments`` use the ADA FHIR
       CodeSystem definition for the image type.
   * - StudyDescription
     - Legacy source data; not read by the generator.
   * - SeriesDescription
     - The default ``SeriesDescription`` for the view.
   * - teeth_example
     - Legacy source data; not read by the generator.

Example record
--------------

.. code-block:: none

   IV01,OrientationRight,LateralityUnpaired,Mouth,,StructureOfBuccalSpace,right,,projection_right,,,,,co,"Intraoral Right Buccal Segment, Centric Occlusion, Direct View",<Progress Name>,Orthodontic Intraoral Series,54^55^16^84^85^46

Maintenance
-----------

Run ``make fetch_resources`` to refresh this file from ``dent-oip``, then run
``make update_resources`` to resolve its bindings and regenerate the committed
terminology lock. Review both diffs before committing.
