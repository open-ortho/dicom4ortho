.. _csv_file_views:

View-layout CSV file
====================

Introduction
------------

The DENT-OIP ``views.csv`` defines the DICOM attribute layout for each of the 73
ADA 1100 image types. The generator downloads it directly from
``https://raw.githubusercontent.com/open-ortho/dent-oip/latest/source/tables/views.csv``.
The packaged ``dicom4ortho/resources/views.csv`` is a compatibility/test snapshot,
not the input to regeneration. Neither file is the bulk-conversion input format
used by the CLI.

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
     - A view-code binding. IV28, IV30, and EV40 require an explicit direction.
       IV29 can omit an unknown direction without losing its known anatomy.
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

Run ``make update_codes`` to download the upstream CSV and the terminology
sources, resolve their bindings, and rewrite the committed terminology lock.
Review the generated diff and run tests before committing. Run ``make check_codes``
to fetch and validate the same inputs in memory, failing on drift without
rewriting the lock. Both commands require network access.

``make fetch_resources`` can refresh the packaged snapshot separately, but the
generator never reads that local copy. To change the authoritative layout,
coordinate the change in ``dent-oip`` rather than editing the snapshot alone.
The removed ``make update_resources`` command should not be used.

For IV29, omitting the unknown direction also omits its nested close-up modifier;
a supplied direction receives that modifier from the current mapping. This is
interim behavior, not a finalized profile rule. The direction policy and modifier
handling remain under discussion in
`dent-oip issue 63 <https://github.com/open-ortho/dent-oip/issues/63>`_.
