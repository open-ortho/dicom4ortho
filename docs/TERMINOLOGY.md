# Terminology pipeline and compatibility baseline

This document records the implementation and regression baseline for PR #70.
It describes the implemented pipeline, not the future versioned ADA-1107
package migration.

## Implemented sources

`tools/generate_codes.py` downloads and resolves the following inputs during
explicit maintenance:

| Input | Source |
| --- | --- |
| DICOM context-group codes | NEMA FHIR ValueSets under `ftp://medical.nema.org/medical/dicom/resources/valuesets/fhir/json/` |
| DCM concept names | `ftp://medical.nema.org/medical/dicom/resources/ontology/DCM/dcm.owl` (RDF/XML, parsed with development-only `rdflib`) |
| ADA 1100 image types | The intraoral and extraoral CodeSystems under `https://terminology.open-ortho.org/fhir/sid/ada1100/CodeSystem/` |
| DENT-OIP view layout | `https://raw.githubusercontent.com/open-ortho/dent-oip/latest/source/tables/views.csv` |

The generator **does not use a pinned `fhir.dicom` package**. It also does not
read the packaged `dicom4ortho/resources/views.csv` for regeneration (the source
snapshot is now at `python/dicom4ortho/resources/views.csv`); that copy
is a compatibility/test snapshot. `make fetch_resources` updates the snapshot
only and is not a prerequisite for regenerating the lock.

The committed `python/dicom4ortho/_generated_codes.py` contains 83 codes, 73 ADA image
types, and 73 resolved views in the reviewed snapshot. Normal builds, unit tests,
and runtime use this lock without fetching terminology. `codes.csv` and
`image_types.csv` are no longer packaged terminology sources.

`SOURCE_PROVENANCE` records each downloaded URL and its observed SHA-256. FHIR
resources also supply version/date metadata; the ontology and CSV are not given
invented versions or dates. The upstream endpoints are mutable: committing the
reviewed output locks application behavior, but does not make a later fetch of
those URLs reproduce the same bytes.

## Maintenance

From the Python source repository with development dependencies installed:

```sh
make update_codes  # Fetch/validate all inputs and rewrite the lock; no commit
make check_codes   # Fetch/validate in memory; fail on drift, without rewriting
```

Both commands require network access. Review generated changes before committing;
source-provenance changes alone can cause drift. The former `make update_resources`
target is removed. Distribution builds use the already committed lock.

## Compatibility and clinical metadata

- Code meanings follow the current official sources and can change textually.
  This does **not** mean all changes preserve the original code values.
- The mirror device changes from SCT `47162009` to SCT `1332162007`, the CID 4072
  intraoral photography mirror.
- SCT `7652006` resolves to `Frenulum labii` in the current NEMA CID 4061 input.
  The earlier local display override is no longer present or needed.
- IV29 has no default direction in the upstream layout. Construction without
  `view_code_keyword` remains supported: mouth/frenum anatomy is retained, while
  unknown direction and its nested close-up modifier are omitted. Explicit or
  later-supplied direction receives the current mapping's nested modifier.
  The direction policy and modifier handling remain a pending profile decision
  in [dent-oip #63](https://github.com/open-ortho/dent-oip/issues/63), not an
  approved new working-group rule. IV28, IV30, and EV40 still require a direction.
- Legacy CSV-only keywords `slap_mark`, `birthmark`, and `direct` are not in the lock.
- CID 4070 treatment events are `PatientRegistration` (SCT `184047000`),
  `OrthodonticTreatmentStarted` (SCT `1332161000`), and
  `OrthodonticTreatmentStopped` (SCT `1340210007`).
- Date-based progress uses a genuine acquisition date. Explicit
  `acquisition_datetime` overrides EXIF `DateTimeOriginal`; editing/digitization
  dates and `ContentDate` are not substitutes. An explicit photograph date can
  also be supplied to `set_treatment_progress_from_date()`.
- Event dates after acquisition and incomplete/conflicting progress metadata
  are rejected. Supplied progress is serialized even without a resolved image
  type, including a zero-day interval.
- The days-based API, `OrthodonticTreatment`, and `Posttreatment` aliases remain
  supported with deprecation warnings until version 2.

## Reviewed lock and validation

The lock at the reviewed source commit `bd1a73549b6bcb26cb814045820713779047bc08`
has SHA-256:

```text
56c9887dd39831b2606a430c15a8bda3a09d357503c9a029a4c3625d59d86f9c
```

The review fixes do not regenerate that file. This is a checksum of committed
bytes, **not** a claim that a fresh network regeneration was performed or that
upstream endpoints are unchanged. Offline generator tests cover deterministic
rendering, provenance validation, and check-mode behavior.

Validation on 2026-10-17 with Python 3.10:

- Non-E2E tests: 94 passed, 4 skipped.
- Changed runtime/test modules and the generator: error-only Pylint passed.
  Full-package Pylint reports two errors at `dicom4ortho/__main__.py:61-62`
  (`unsupported-assignment-operation` on `PrettyTable.align`) in unchanged code
  with the installed dependencies; these review fixes do not address them.
- Source archive and wheel (built from the source archive): passed.
- Companion `gh-pages` Sphinx HTML build with warnings as errors: passed.
- Docker/Orthanc E2E tests: not run; Docker is unavailable in this container.
- Live terminology drift check: not run; the reviewed lock was kept unchanged.

## Future ADA-1107 package migration

[dent-oip #56](https://github.com/open-ortho/dent-oip/issues/56) tracks publishing
versioned ADA-1107 mappings; [dent-oip #11](https://github.com/open-ortho/dent-oip/issues/11)
tracks upstream terminology compilation. Neither package consumption nor a
package checksum pin is implemented by this PR.

When that package is available, pin its version/checksum and compare its generated
output against the reviewed lock and the runtime regression tests before replacing
the current resolver. Preserve all 73 view mappings, canonical treatment events,
acquisition-time precedence and validation, supported deprecated APIs, offline
runtime/build behavior, and actual coding/sequence semantics. Do not restore a
guessed IV29 direction or a removed display override merely to reproduce an older
PR description. Profile mapping ownership remains with DENT-OIP; canonical
publication belongs at `terminology.open-ortho.org`.
