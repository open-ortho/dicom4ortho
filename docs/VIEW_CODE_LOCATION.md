# Photograph-type code location

Both implementations write photograph prescription codes under
`RequestAttributesSequence (0040,0275)` → `ScheduledProtocolCodeSequence (0040,0008)`.
This follows [DENT-OIP #12](https://github.com/open-ortho/dent-oip/issues/12) and
[current §3.4.1.3](https://open-ortho.github.io/dent-oip/nightly/V1_Orthodontic_Imaging_Profile/03_oip_process_flow/index.html#image-views-request-procedure-codes).
The list describes requested protocols, not proof that every listed view was acquired.
Projection stays in the single View Code Sequence item. Image Comments remains a
human-readable label, not a machine-readable identifier. No projection CID 4063
extension is manufactured for a scheduled protocol.

Creation with a known view and no supplied protocol list creates a one-code request.
With worklist/series protocols, preserve the supplied list, order, repetitions, code
metadata and request identifiers instead of replacing it with this instance's view.
Applications creating several images in one series should supply the same series
request context to each. The library does not gather sibling images automatically.

Swift `extractViews` returns every qualifying request/worklist occurrence with indices
and a prescribed role, including unresolved qualifying codes. It does not infer a
unique actual view from a series list or use Instance Number as an array index.
Instance-level identification remains the separate question in
[DENT-OIP #25](https://github.com/open-ortho/dent-oip/issues/25).

Python's existing `image_type_code_dataset` / `get_image_type_code_dataset` convenience
returns a code only for one qualifying occurrence. With multiple prescriptions it
returns `None` and logs ambiguity rather than guessing; use the native dataset to
inspect the full list. The setter preserves unrelated codes and request metadata:

```python
OrthodonticPhotograph.set_image_type_code_dataset(
    dataset, code, request_index=0, protocol_index=1)
```

Indices are zero-based; explicit selection is required for ambiguous lists. The
historical `creator_uid` argument is accepted only with a supplied private extension
context: flag `Y`, Context Identifier, Mapping Resource, Context Group Version and
Local Version. An orphan creator UID (argument or embedded field) or an incomplete
extension is rejected before the destination changes. Ordinary protocol codes omit
extension attributes; no projection CID 4063, default creator or current-date version
is invented. Valid supplied coded metadata is copied intact.
Legacy private View Code Sequence declarations remain readable; writers no longer
append type codes there. Existing files are not bulk-migrated or silently rewritten.

The old `latest` documentation tag points to August 2024, before #12's January 2025
implementation. The [issue findings](https://github.com/open-ortho/dent-oip/issues/12#issuecomment-6326356779)
record the historical/current source links; the instruction was not missing from
the current document.
