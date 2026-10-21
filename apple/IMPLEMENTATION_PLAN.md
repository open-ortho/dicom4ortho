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
- Create complete images and image-free templates; write photograph-type codes under
  Request Attributes / Scheduled Protocol Code Sequence as DENT-OIP #12 directs,
  keeping projection separate and retaining supplied series-level prescriptions.
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
checks, and CI/release documentation. The request-code correction below supersedes
the earlier structured-comment extraction design.

PR1: https://github.com/open-ortho/dicom4ortho/pull/85. Formal reviewer requests are
not permitted for zgypa-agent, so @zgypa received a PR comment notification instead.

See [QUALIFICATION.md](QUALIFICATION.md) for results and unmet acceptance checks.
Do not mark #82 completed while simulator execution or another required check remains blocked.
PR2: https://github.com/open-ortho/dicom4ortho/pull/86. @zgypa received the second
review notification there. The two PRs target develop; PR2 includes PR1 and should
be reviewed/merged after the API PR. Follow-up qualification fixes continue on PR2.

## Environmental limit

mainframe1 is reachable as the separately provisioned `amagni-agent` build user.
Xcode 26.3 cannot resolve a tools-6.4 package for simulator testing. Continue using
isolated Swift 6.4.1 and available SDKs without upgrading host software. No Linux
qualification, complete profile conformance, or iOS simulator execution is implied.

## View-code placement correction

The maintainer requested that both Python and Swift use DENT-OIP #12's
`RequestAttributesSequence.ScheduledProtocolCodeSequence` location. The instruction
is present in current source and nightly §3.4.1.3; inspecting the old August 2024
`latest` tag had incorrectly suggested it was missing. January 20, 2025 commit
`5d3fb8a35` supports #12's closure. Findings and reciprocal links were added to
[issue 12](https://github.com/open-ortho/dent-oip/issues/12#issuecomment-6326356779) and
[issue 25](https://github.com/open-ortho/dent-oip/issues/25#issuecomment-6326362717).

New output uses coded request protocols; comments are labels only and private
projection extensions are read-only legacy input. Supplied protocol lists, codes,
identifiers and request/procedure context survive. Neither implementation infers
an actual image type from an ambiguous list or treats Instance Number as a code index.
This explicitly authorized Python behavior change supersedes the earlier promise
of an unchanged Python runtime; packaging and entry points remain unchanged.
