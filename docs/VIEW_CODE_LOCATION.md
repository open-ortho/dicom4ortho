# Intended photograph type: proposed instance-level encoding

The maintainer's [2026-10-23 review of PR #86](https://github.com/open-ortho/dicom4ortho/pull/86#pullrequestreview-5626642043)
supersedes the earlier use of Request Attributes / Scheduled Protocol Code Sequence
as a photograph identifier. Those codes describe a series/request, while different
images in that series need their own photograph-type designation.

## Swift proposal

Follow [DENT-OIP #25's instance-level Acquisition Context proposal](https://github.com/open-ortho/dent-oip/issues/25#issuecomment-6340377599):

```text
AcquisitionContextSequence (0040,0555)
  Item
    ValueType (0040,A040) = CODE
    ConceptNameCodeSequence (0040,A043)
      (AAAAAAA, DCM, "Intended orthodontic photographic view")
    ConceptCodeSequence (0040,A168)
      the selected ADA-1100 photograph-type code and its existing coding scheme
```

**`AAAAAAA` is a provisional CP-style placeholder, not an assigned DCM code.**
The proposed concept and TID 3465 addition still need WG-22 agreement and DICOM CP
approval. The implementation reuses existing DICOM attributes; it does not invent a
tag or claim that a new standard code/profile rule has already been adopted.
`DentalProfile.intendedViewConcept` keeps the provisional identity in one place,
outside the reviewed authoritative terminology lock.

The concept records the view clinical staff **intended** to acquire for this image.
For example, an attempted smiling view remains that intended view even if the patient
could not smile. It does not prove that every specified pose/condition was achieved.

Swift creation and pixel-free templates add one such item without replacing the
other clinical Acquisition Context items. Different instances can have different
intended views while sharing study/series UIDs and the exact same request context.
Projection remains the single `ViewCodeSequence` item; Image Comments is a label,
never the source of machine-readable view extraction.

## Extraction and prescriptions

`extractViews` returns every qualifying occurrence with its original coded dataset:

- `.intended(acquisitionContextIndex:)`: the proposed per-instance concept.
- `.image(viewCodeIndex:)`: read-only compatibility with legacy private View Code
  Sequence declarations; no new photograph type is appended to that sequence.
- `.scheduled(stepIndex:protocolIndex:stepID:)` / `.requested(requestIndex:protocolIndex:)`:
  supplied worklist or copied series/request prescriptions, not instance identity.

Indices are zero-based, duplicates remain distinct, and unknown qualifying values
are retained with a nil catalog keyword. Extraction checks concept/code identity,
not Code Meaning, comments, anatomy, pixels or filenames. Unrelated Acquisition
Context concepts and incomplete/non-CODE items do not become intended views.

Supplied protocol lists, versions, order, repetitions and request identifiers remain
unchanged. New image/template creation never fabricates a scheduled/performed protocol
from its intended view, chooses a view by Instance Number, or promotes a prescription
to performed evidence. Existing datasets are not bulk-migrated.

## Python is separate

PR #86 leaves `python/`, its existing tests and the shared `tools/generate_codes.py`
unchanged from `develop`. The previous Python request-code/creator changes are not
part of the Swift delivery. [Issue #88](https://github.com/open-ortho/dicom4ortho/issues/88)
tracks Python alignment and the required legacy/migration decisions separately.
This document does not claim that Python already writes or reads the new concept.

The Apple-only maintenance tool `apple/Tools/export_terminology.py` reads the existing
reviewed lock to export/check Swift's resource offline. It never rewrites the Python
lock or changes existing Make commands; neither Python nor the exporter is a Swift
runtime or normal SwiftPM-build dependency.
