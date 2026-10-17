Terminology sources
===================

``dicom4ortho`` uses official FHIR terminology at maintenance time and a
committed generated module at runtime. The generated
``dicom4ortho/_generated_codes.py`` module is the terminology lock for a
release. It records source provenance and contains the resolved DICOM codes,
all 73 ADA image types, and the complete view definitions.

Normal package builds, tests, and application use read this committed lock.
They do not download terminology or require network access.

Authoritative sources
---------------------

The generator resolves explicit code bindings from these sources:

* DICOM context-group codes come directly from NEMA FHIR ValueSets under
  ``ftp://medical.nema.org/medical/dicom/resources/valuesets/fhir/json/``.
* DCM concept names come from NEMA's RDF/XML ontology at
  ``ftp://medical.nema.org/medical/dicom/resources/ontology/DCM/dcm.owl``.
  The generator uses the development-only ``rdflib`` dependency to parse it.
* ADA 1100 intraoral and extraoral image types come from the FHIR CodeSystems
  published under ``https://terminology.open-ortho.org/fhir/sid/ada1100/CodeSystem/``:
  ``intraoral-2d-photographic-scheduled-protocol`` and
  ``extraoral-2d-photographic-scheduled-protocol``.
* The draft ANSI/ADA-1107 view layout is downloaded from its source repository at
  ``https://raw.githubusercontent.com/open-ortho/dent-oip/latest/source/tables/views.csv``.
  Regeneration does not read ``dicom4ortho/resources/views.csv``; that packaged
  snapshot remains available for compatibility and offline binding tests.

The profile will be published as ANSI/ADA-1107. Its source repository is still
named ``dent-oip``; the existing source and issue URLs remain unchanged.

The old ``codes.csv`` and ``image_types.csv`` files are no longer terminology
sources and are not packaged.

The generator no longer downloads a pinned ``fhir.dicom`` package. These upstream
endpoints can change: it is the reviewed, committed output that is locked.
``SOURCE_PROVENANCE`` records each observed URL and the SHA-256 of the downloaded
bytes, plus ``version`` and ``date`` when supplied by a FHIR resource. No version
or publication date is invented for the DCM ontology or the view-layout CSV.

SCT ``7652006`` uses the current CID 4061 display, ``Frenulum labii``. The generator
does not apply the display override used by an earlier implementation.

Updating the lock
-----------------

Install the development dependencies, then fetch all terminology sources and
the upstream view-layout CSV from the Python source repository:

.. code-block:: bash

   pip install -e ".[dev]"
   make update_codes

This command rewrites ``dicom4ortho/_generated_codes.py``. It does not commit
the result. Review the generated diff and run the tests before committing it.

To fetch and validate the same upstream inputs without rewriting the lock:

.. code-block:: bash

   make check_codes

``make check_codes`` regenerates in memory and exits nonzero when the result
differs from the committed file. It can be run manually or in scheduled drift
checks; provenance-only changes can also produce a difference. Both maintenance
commands require network access and can fail if a source is unavailable.

``make fetch_resources`` only refreshes the packaged CSV snapshot. It is not a
prerequisite for ``make update_codes`` and does not change which CSV the generator
downloads. The old ``make update_resources`` command has been removed.

Normal package builds and runtime use the committed lock without contacting any
of these sources. A future versioned ANSI/ADA-1107 profile package is planned in
`ANSI/ADA-1107 issue 56 <https://github.com/open-ortho/dent-oip/issues/56>`_; consuming
that package is not part of the current source pipeline.
