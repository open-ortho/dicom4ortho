# Issue #82 delivery record

The source branch `feature/82-swift-materialization` is retained as reference, not
merged. The clean branches start from `develop` without Python/package restructuring.

## PR1 — `zgypa-agent/82-swift-api`

- Define compilable application-facing values and clinical operation signatures.
- Expose DICOMKit datasets directly (user-confirmed decision).
- Keep missing operations explicitly throwing; no fabricated DICOM output.
- Document lifecycle, clinical roles, template incompleteness, source preservation,
  extraction scope, identity sharing, toolchain requirements, and known blockers.
- Validate the public surface on the existing isolated Apple toolchain.
- Request review from `zgypa`; continue to PR2 without waiting for another prompt.

Validated 2026-10-21: the clean package resolves DICOMKit 2.7.0 and its dependency
graph recorded in `Package.resolved`. Three API-surface tests pass on mainframe1
with isolated official Swift 6.4.1 (arm64 macOS). All nine existing Python repository
layout tests pass. These checks do not establish clinical implementation conformance.

## PR2 — `zgypa-agent/82-swift-implementation`

- Implement the unchanged PR1 interfaces, reusing reviewed backend/profile code.
- Bundle offline terminology generated from the same inputs as Python, without
  refreshing the clinical lock just to build and without adding a Python runtime dependency.
- Create complete images and image-free templates; write the intended photograph
  type in instance-level Acquisition Context using the provisional DENT-OIP #25
  concept, keeping projection and supplied series-level prescriptions separate.
- Extract image declarations and every worklist step/protocol occurrence; preserve
  role/association and unknown qualifying codes; exclude unrelated projections.
- Implement supported local image imports, EXIF fallback, clinical metadata, worklist
  copying, stable identity, serialization, and separate compressed preservation.
- Test the three capabilities through thin adapters and independently validate output.
- Publish a capability matrix distinguishing encoding, decoding, and preservation.
- Run available Apple/Python checks; do not call simulator cross-builds simulator tests.
- Add CI/release guidance and request PR review. Keep #82 open for any unmet criteria.

## Implementation checkpoint (2026-10-21)

The three public capabilities are implemented, with an offline 73-view catalog,
clinical/worklist metadata, stable identity, supported image imports, separate
compressed preservation, 13 output encodings, contract adapters, independent output
checks, and CI/release documentation. The instance-level correction below supersedes
both the structured-comment and the series-level request-code experiments.

PR1: https://github.com/open-ortho/dicom4ortho/pull/85, merged into `develop` as
`410f9d4`. Formal reviewer requests are
not permitted for zgypa-agent, so @zgypa received a PR comment notification instead.

See [QUALIFICATION.md](QUALIFICATION.md) for results and unmet acceptance checks.
Do not mark #82 completed while simulator execution or another required check remains blocked.
PR2: https://github.com/open-ortho/dicom4ortho/pull/86. @zgypa received the second
review notification there. PR2 merges the current `develop`, retaining the real
implementation, offline resources/codecs and real-result tests
instead of restoring API-only placeholders. Follow-up qualification fixes continue on PR2.

## Environmental limit

mainframe1 is reachable as the separately provisioned `amagni-agent` build user.
Xcode 26.3 cannot resolve a tools-6.4 package for simulator testing. Continue using
isolated Swift 6.4.1 and available SDKs without upgrading host software. No Linux
qualification, complete profile conformance, or iOS simulator execution is implied.

## Instance-level placement correction (2026-10-23)

The maintainer's [new review](https://github.com/open-ortho/dicom4ortho/pull/86#pullrequestreview-5626642043)
rejects series-level request protocols as image identifiers and directs implementation
of [DENT-OIP #25's Acquisition Context proposal](https://github.com/open-ortho/dent-oip/issues/25#issuecomment-6340377599).
New Swift output records **Intended orthodontic photographic view** with the explicitly
unassigned CP-style concept `(AAAAAAA, DCM, ...)` and the selected ADA catalog value.
It reuses Acquisition Context, preserves the other clinical rows, and does not
assert that the patient achieved every intended pose. Supplied protocol lists and
request identifiers remain unchanged and separately labeled. Comments are labels only;
private projection declarations are legacy read input, not newly written.

All changes to `python/` and the shared `tools/generate_codes.py` are removed from
this PR relative to `develop`. The Apple-only exporter reads the unchanged lock;
normal Swift builds stay offline. Python alignment is a separate issue, [#88](https://github.com/open-ortho/dicom4ortho/issues/88).
Earlier request-code and Python-runtime validation results are historical and do
not qualify this revised representation. WG-22/CP agreement and simulator execution
remain unverified; do not close #82 or claim an assigned DICOM concept.
