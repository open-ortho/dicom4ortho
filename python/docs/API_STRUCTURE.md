# Python API structure and compatibility binding

Draft for [#83](https://github.com/open-ortho/dicom4ortho/issues/83), 2026-10-20.
The shared [functional requirements](../../docs/API_CONTRACT.md) and
[structural definition](../../docs/API_DEFINITION.md) are separate authorities.

## Preserve the existing working-record model

```text
DicomBase                    native dataset, identity, clinical fields, output
  PhotographBase             image ingestion/preservation and EXIF
    OrthodonticPhotograph    profile, type code, direction, treatment progress

OrthodonticStudy -> OrthodonticSeries -> existing photograph objects
OrthodonticController        conversion/batch/CLI conveniences around those models
```

Sources: [model.py](../dicom4ortho/model.py),
[m_orthodontic_photograph.py](../dicom4ortho/m_orthodontic_photograph.py),
[controller.py](../dicom4ortho/controller.py).
This hierarchy need not be imposed on other languages or refactored for aesthetics.

| Concern | Python compatibility obligation |
| --- | --- |
| Construction | Keep `OrthodonticPhotograph(**metadata)`, empty/templates, unknown types, existing keys/defaults/accepted formats |
| Dataset | `to_dataset()` returns the live native dataset; arbitrary raw edits do not reconstruct retained profile/progress state |
| Edits | Keep existing properties and profile/direction/progress functions |
| Profiles | `applyProfile` maps to `set_dicom_attributes_by_type_keyword(type_keyword=None)`; no new runtime alias is necessary |
| Names | `patientFirstName` maps to `patient_firstname`, not a new `patient_first_name`; likewise provider/operator names |
| Type codes | Keep the property and static first-code getter/setter, including preservation of unrelated items |
| Output | Keep `prepare`, `save`, `load`, save-syntax helpers and stored destination; `to_byte()` returns a rewound `io.BytesIO` |
| Identity | Preserve existing registered roots and missing/colliding hierarchy repair; do not replace valid SOP identity |
| Grouping | Retain ordered live children and existing propagation timing |
| Adapters | Keep controllers, CSV/CLI and existing transport entry points outside the shared core |
| Deprecations | Existing aliases/day-offset warnings and removal policy stay; new renames require forwarding wrappers and focused warning tests |

The IDL names identify capabilities. Its Python binding is not a replacement
runtime API or a demand that consumers adopt generated models.

## Boundaries that must not silently change

- **Metadata precedence:** explicit constructor acquisition overrides EXIF fallback;
  later operations may replace earlier facts. Equipment EXIF, MWL copying and
  profile descriptions have operation-specific rules, not one universal merge rule.
- **Preparation:** photograph `save()` currently prepares via override and base
  paths. `to_byte()` repairs identities without full photograph preparation.
  Consolidating these paths can change observable metadata and is not required here.
- **Grouping:** series `add()` retains a photo without assigning parent identities;
  study `add()` sets the series StudyUID; series `save()` propagates IDs/description
  onto the original photos. Do not move those effects earlier for naming consistency.
- **Drafts:** `prepare()` is not complete clinical validation. Unknown-view logging
  is not equivalent to invalid-treatment-date rejection or missing required direction.
- **Native types:** getter/setter accepted types can differ, especially date/time
  and DICOM values. The structural prototype deliberately avoids claiming all these
  legacy surfaces are already fully annotated or checked.

Known narrow correctness candidates are separate from naming: the manufacturer's
getter uses a lowercase dataset keyword, and the image-bytes setter does not
implement its advertised bytes path. Fixing either needs a focused regression and
review; adding structural annotations does not repair or certify those behaviors.

## Additive all-declaration extraction

`get_image_type_code_dataset(ds)` currently returns the first `ViewCodeSequence`
item with the proprietary CID/extension flag. It does not catalog-resolve or walk
all worklist steps. The deprecated `get_scheduled_protocol_code()` aliases that
getter despite its name. `OrthodonticController.get_image_view_code()` is a stub.

The IDL's `ViewTypes.extractDeclaredViewTypes` is a **new requirement**, not an
assertion that Python already implements it. Keep the single-result APIs intact.
Implement extraction separately against already parsed datasets. Local tests need
multi-step/multi-code image/MWL fixtures, scheme/version collisions, qualified
unknown/private candidates, malformed entries, absent declarations, repeated
occurrences, source associations and scheduled-versus-image role separation.
No hidden anatomical inference or network querying belongs in that operation.

## Bounded changes in this PR

The executable structural prototype checks selected existing photograph properties,
type-code helpers, profile/direction operations, dataset access, preparation and
classifiers. It adds accurate annotations for that subset, including the already
accepted nullable code/creator arguments. No runtime name, default, body, UID root,
DICOM tag, transfer syntax or grouping behavior needs to change.

The tests distinguish structural checking (including unimplemented bodies) from
ordinary Python behavior checks. They do not certify the entire draft IDL or the
unfinished extraction operation. Existing model/photography/terminology/image tests
remain the implementation's behavioral tests. Production consumers are outside this
repository; passing local tests is not evidence about all their undocumented usage.
