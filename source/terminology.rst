Terminology sources
===================

``dicom4ortho`` uses official FHIR terminology at maintenance time and a
committed generated module at runtime. The generated
``dicom4ortho/_generated_codes.py`` module is the terminology lock for a
release. It records the source versions and contains the resolved DICOM codes,
all 73 ADA image types, and the complete view definitions.

Normal package builds, tests, and application use read this committed lock.
They do not download terminology or require network access.

Authoritative sources
---------------------

The generator resolves explicit code bindings from these sources:

* DICOM codes and DCM concept names come from the official ``fhir.dicom``
  package published at ``https://fhir.org/packages/fhir.dicom``. The package
  version is pinned in ``tools/generate_codes.py``.
* ADA 1100 intraoral and extraoral image types come from the FHIR CodeSystems
  published by ``https://terminology.open-ortho.org``.
* ``dicom4ortho/resources/views.csv`` remains the local source for the layout
  of DICOM attributes associated with each view. It is derived from the
  ``dent-oip`` project.

The old ``codes.csv`` and ``image_types.csv`` files are no longer terminology
sources and are not packaged.

The current development lock records DICOM FHIR package version
``2025.3.20250714`` and ADA CodeSystem version ``2.0.0``.

Updating the lock
-----------------

To fetch the official FHIR resources and regenerate the lock, run this from
the source repository:

.. code-block:: bash

   make update_resources

This command rewrites ``dicom4ortho/_generated_codes.py``. It does not commit
the result. Review the generated diff and run the tests before committing it.

Updating ``views.csv`` is a separate, explicit operation:

.. code-block:: bash

   make fetch_resources
   make update_resources

This separation prevents normal package builds from changing source files or
depending on upstream services.
