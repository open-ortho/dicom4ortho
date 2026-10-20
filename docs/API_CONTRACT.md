# Language-neutral functional requirements

**Draft 0.2, 2026-10-20 — for review in [#83](https://github.com/open-ortho/dicom4ortho/issues/83).**

A photograph is a **mutable DICOM working record**, progressively enriched with
image evidence, clinical facts and profile mappings, then prepared for output.
These requirements originated during #82. They describe clinical meaning and
ownership, not a required class hierarchy or literal spelling in every language.
The separate [interface definition](API_DEFINITION.md) describes structural checks.
Each implementation keeps its own behavioral tests; no shared behavioral DSL is required.

## C01 — A photograph is a working record

Construction supports an empty record, an image-type template, or an image with
known metadata. Missing pixels, an unresolved type or omitted optional clinical
facts do not prevent progressive editing. They do not establish readiness for
clinical exchange either. An unreadable supplied image or contradictory inputs
are different from omitted inputs. Construction does not save or send anything.

**Why:** patient, context and image data may arrive separately; demanding all inputs
up front would eliminate existing Python templates and staged workflows.

## C02 — Dental conveniences edit an accessible native dataset

The record exposes its native DICOM dataset for advanced use. Edits affect that
working record, not a detached snapshot. Bindings need not introduce a second
generic DICOM object model or mirror Python's inheritance.

Convenience getters/setters deliberately use familiar dental vocabulary, which is
not always DICOM's broader terminology. Document the translation, not just the name:

| Dental/application concept | DICOM concept | Must not be confused with |
| --- | --- | --- |
| Responsible dental provider | Physicians of Record `(0008,1048)` | Referring or performing physician |
| Person acquiring the photograph | Operators' Name `(0008,1070)` | Scheduled performing physician |
| Photograph type/profile | ADA photograph identity and its reviewed mappings | A projection/direction alone |
| Actual acquisition time | Acquisition Date/Time/DateTime | Content/editing time |

Patient, personnel, identity, time and profile edits should not require callers to
assemble ordinary DICOM sequences. Profile/progress state may also live alongside
the dataset. A high-level edit may rebuild its documented managed sequences;
arbitrary raw edits do **not** imply automatic reconstruction of retained state.

**Why:** familiar terms reduce integration errors only if clinically distinct roles
remain distinct. The native dataset escape hatch accommodates uncommon attributes
without requiring a new wrapper for every DICOM tag.

## C03 — Profiles enrich facts; declared-type extraction is not inference

Applying a recognized photograph profile uses the reviewed offline terminology for
anatomy, orientation where known, devices, descriptions, view/modifiers and
acquisition context. A type and its viewing direction are distinct. Unknown types
can remain unresolved without invented mappings. Required variable direction must
be supplied or reported missing; IV29's unknown optional direction stays unknown.
Treatment context can exist independently of a resolved type.

Reading/replacing the embedded photograph-type code is separate from applying a
whole profile. Replacing a private-extension code preserves unrelated code items
and identifies the extension creator. It must not silently apply another profile.

### Read-only extraction of all declared photograph types

An extraction operation accepts a supplied image-instance or Modality Worklist
dataset without constructing a photograph, reading pixels, mutation or networking.
Callers should not need to know sequence layouts or catalog-resolution rules.

- Inspect supported image declarations, including qualifying private-extension
  items in `ViewCodeSequence`; a projection there is not itself an ADA photo type.
- Inspect **every** `ScheduledProcedureStepSequence[*]` and every corresponding
  `ScheduledProtocolCodeSequence[*]`, not just the first step/code. Not every
  protocol denotes an individual photograph.
- Inspect supported copied scheduled codes under `RequestAttributesSequence` in
  image instances. Keep them labelled as scheduled context, not actual image type.
- Document supported IOD-specific locations and unsupported contexts. Do not
  recursively treat every arbitrary DICOM code sequence as a type declaration.

Return structured occurrences and diagnostics, preserving:

| Information | Meaning |
| --- | --- |
| Original identity | Code value and its representation, scheme, optional version/meaning, relevant extension creator/context metadata |
| Resolution | Recognized bundled photograph keyword or explicit unresolved status |
| Role | Image-instance declaration versus scheduled/copied requested context |
| Source | Sequence path and item indices, procedure-step identifiers where supplied |
| Classification | Recognized, unresolved candidate, unrelated projection/protocol, malformed/incomplete entry |

Resolve using code/scheme/version and applicable extension rules, **not** display
meaning or an `EV`/`IV`-looking value alone. Preserve qualifying private/unknown
candidates as unresolved; unrelated entries may be separately classified. Report
malformed entries without losing valid declarations elsewhere. Preserve occurrence
order within each context and repeated declarations across steps/roles. A unique
projection, if offered, is an additional operation. No declarations means an empty
declaration list, not a fabricated default; diagnostics and separately classified
other entries may still be present. Unsupported contexts must not masquerade as
successful exhaustive extraction.

Do not infer a type from anatomy, projection, free text or filenames. Future
inference must be a separate API with evidence/ambiguity and distinct results.
Resolving an explicit code against the catalog is extraction, not inference.

**Why:** a first-match getter loses information; requested photographs are not proof
of what an actual image shows. Existing first-result Python helpers remain supported.

## C04 — Clinical roles, time and source precedence are explicit

Keep patient, responsible dental provider, operator, referring and performing
physician roles distinct. Copy applicable supplied-MWL metadata **offline**, without
authorizing a worklist query. Requesting/scheduled-performing roles are not operators.

Explicit acquisition input takes precedence over EXIF acquisition fallback.
DateTimeOriginal can supply missing acquisition time; digitization/editing dates
cannot substitute. A deliberate later metadata operation may overwrite earlier
values. There is no global rule that constructor arguments outrank every later
worklist/profile edit. Equipment EXIF precedence is operation/binding-specific.

Treatment progress uses a clinical event and elapsed **calendar days** from event
date to genuine acquisition date, with an explicit date override where needed.
Zero is valid; future events or missing reference dates are errors. A date without
time of day must not change because of timezone conversion. Replacing progress
replaces managed context instead of accumulating duplicate events/offsets. Python
retains its precomputed-day APIs and their existing deprecation policy.

**Why:** role confusion and editing timestamps can yield clinically false metadata
even in a syntactically valid file. A global merge rewrite would change production flows.

## C05 — Image ingestion preserves evidence

Support memory and local-file input without requiring an output path. Declare
formats/layouts and support gaps per implementation. Preserve supported compressed
codestreams when possible; removing a container for DICOM is not recompression.
Decoding, preservation and encoding a new representation are separate capabilities.
Additional lossy encoding must be explicit and recorded in compression/derivation
history. A transfer-syntax label must truthfully describe stored pixel data.

**Why:** silent recompression damages evidence. Broad codec support is not grounds
to replace ordinary file/byte workflows or promise unsupported codecs.

## C06 — Complete identity deliberately; do not churn it on output

SOP identity belongs to the photograph; series/study UIDs establish relationships.
Preserve valid distinct caller identities. Preparation supplies missing hierarchy
identity under registered roots; repeated unchanged output must not replace SOP
identity or recompress evidence. Private codec intermediates do not replace the
final published instance's UID. Keep dataset and File Meta identities consistent.

Python's missing/colliding hierarchy-UID repair remains compatible and diagnosed.
New bindings declare repair/reject policy; neither may silently replace valid
relationships. A new derivation of a published instance needs a separately declared
identity policy. Random suffix algorithms need not match; promised deterministic
UID mappings do.

**Why:** identity churn creates duplicate instances and breaks clinical references.

## C07 — Study/series groups retain ordered live records

A series groups photographs; a study groups series, in insertion order. They retain
the **same logical working objects**, not invisible snapshots. Adding does not save
or send. Identity/description propagation occurs at documented boundaries; a caller
holding a child sees grouping edits. Python's deferred series propagation and study
attachment timing remain compatible. Do not add implicit deduplication, single-parent
ownership, all-or-nothing transactions or a new naming policy as API cleanup.

**Why:** grouping copies can leave the caller inspecting identities different from
those in saved files. Logical shared mutation need not imply identical memory models.

## C08 — Preparation, dataset access, serialization and saving are distinct

Preparation completes managed defaults, hierarchy identity and applicable fallbacks.
It is repeatable for unchanged valid records, not a freeze, a clinical validator or
permission to invent facts. Editing/repreparing remains possible. Expose live native
dataset access, memory serialization and local-file output without requiring a path
for memory workflows. Document implicit preparation/mutation in output conveniences.

Python's `save()` versus `to_byte()` preparation differences remain compatibility
facts, not a universal rule. Its memory result is a positioned `io.BytesIO`, not raw
`bytes`; other languages may use their native byte container. Output must not add
implicit compression. Saving is not networking; successful serialization does not
certify a complete IOD/profile, especially for drafts.

**Why:** callers need drafts and in-memory output without temporary files or delivery.

## C09 — Distinguish incomplete, invalid, unsupported and operational failure

Missing optional facts/unresolved types leave a draft, not fabricated metadata.
Contradictory treatment input, unreadable images, unsupported encodings/layouts and
I/O failures are distinct. Expose native diagnostics/errors with recovery policy.
Preserve Python's existing warning/no-op/error distinctions unless a specific
compatibility change is justified and tested. New languages need not clone Python
exception names or warning text. Strict validation is an explicit capability.

**Why:** blanket rejection prevents templates; swallowed failures falsely imply success.

## C10 — Adapters and legacy helpers are not a second core model

Controllers, CSV/CLI, default paths, UID helpers and deprecated aliases can adapt
the working record. Preserve Python production entry points; do not require an MVC
hierarchy, a universal materialization service or 89 mechanically copied declarations.
Network delivery/authentication/queues are outside the shared native-library core;
Python's existing transport functionality is not removed. Offline MWL copying is in scope.

**Why:** separating responsibilities in the contract does not require reorganizing
tested Python runtime code without a functional benefit.

## Adoption and completion

Use the existing Python API where it fits. A narrowly justified cleaner operation
may replace a historical spelling only with an old-signature forwarding wrapper,
preserved return/default/error behavior and tested `DeprecationWarning`. No rename
is required simply to match another language. Follow [Python binding notes](../python/docs/API_STRUCTURE.md).

Structural conformance checks declarations only. Correctly declared unimplemented
bodies may pass. Each language retains its unit/integration/clinical validation;
neither a structural pass nor this draft means full functional completion. Completing
all-declaration extraction and the Swift working-record port remains separate work.
