# Shared functional contract

dicom4ortho implementations share functionality and DICOM/DENT-OIP requirements,
not a prescribed public API or internal design. The notation below describes
capabilities, not required method names or signatures. A view is an orthodontic
photograph type from the DENT-OIP/ADA 1100 mappings.

## Operations

```text
create(image, metadata, view) -> DICOM image
create_stub(view) -> DICOM dataset template
extract_views(DICOM) -> views
```

`create_stub` produces a view-populated template. Without pixels or other required
clinical metadata, it is not necessarily a complete, exchange-ready DICOM image.

`extract_views` reads the photograph types declared in a supplied DICOM dataset,
without making consumers navigate nested DICOM sequences:

- For an image instance, return its declared view type(s), typically one.
- For a Modality Worklist, return all prescribed view types across all scheduled
  procedure steps and protocol-code items, not just the first match.
- Return a collection consistently; if no declared views are found, it is empty.
- Read the supplied dataset only: no network queries or inference from pixels,
  anatomy, filenames or other undeclared evidence. Worklist views are prescriptions,
  not proof that photographs were acquired.

## Adapters and conformance

Each implementation must expose these capabilities through a thin test adapter.
The adapter translates test inputs and results and calls the actual implementation;
it must not supply missing clinical functionality. Public APIs may be language-idiomatic.

Shared reference cases and DENT-OIP validation rules, including the Gazelle X
Validator (GXV) work in [dent-oip#64](https://github.com/open-ortho/dent-oip/issues/64),
will assess functional conformance when available. Tests must check extraction
results as well as DICOM outputs, with separate expectations for incomplete templates.
Until that shared suite exists, implementations continue with their own tests;
shared conformance is not yet established. This contract does not claim that every
existing implementation already provides every capability.
