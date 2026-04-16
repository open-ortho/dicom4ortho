Usage
=====

The DICOM images require a lot of information which is not contained in
a flat PNG or JPEG image. This information would, in a production
environment, usually come from the practice management software, or
photo management software.

CLI
----

The current way to feed this information to ``dicom4ortho``\ ’s CLI is
using a CSV file. You can find an example CSV file
`here <resources/example/input_from.csv>`__

Once installed, use dicom4ortho like this:

.. code-block:: bash

   $ dicom4ortho <filename>

Where ``filename`` should be a ``.csv`` file. Passing a single image
file with metadata through arguments is planned for future
implementations.

Using the library directly
---------------------------

Latest example of usage can be found in the ``fhir2dicome4ortho.tasks`` module.
Also look at the main entrypoint for ``dicom4ortho``.

Updating terminology codes
--------------------------

The DICOM codes and orthodontic view definitions used by ``dicom4ortho``
are baked in at build time as a generated Python module
(``dicom4ortho/_generated_codes.py``). This is intentional: it acts as a
lock file that pins the exact terminology used in a release, ensures
reproducible builds, and means end users never need network access at
runtime.

To update the codes (e.g. when DICOM publishes new CID tables or
``dent-oip`` updates its view definitions), run the following from the
repository root:

.. code-block:: bash

   $ make update_resources

This will:

1. Download the latest ``codes.csv`` and ``views.csv`` from the
   ``dent-oip`` repository.
2. Regenerate ``dicom4ortho/_generated_codes.py`` from those sources.
3. Commit the updated files.

The sources for the codes are:

- **View layout** (which codes apply to each of the 73 orthodontic views):
  ``dent-oip`` repository on GitHub
  (``https://raw.githubusercontent.com/open-ortho/dent-oip/latest/source/tables/``)
- **DICOM CID codes** (CID 4061–4072, added by CP-1570): published by DICOM
  as FHIR ValueSets at
  ``ftp://medical.nema.org/medical/dicom/resources/valuesets/fhir/json/``
- **Orthodontic SNOMED codes**: ``terminology.open-ortho.org``
