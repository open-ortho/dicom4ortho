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
- Create complete images and image-free templates; write explicit coded photograph
  declarations using DENT-OIP's structured Image Comments format so creation/extraction
  can be tested together without violating View Code Sequence's single-item constraint.
- Extract image declarations and every worklist step/protocol occurrence; preserve
  role/association and unknown qualifying codes; exclude unrelated projections.
- Implement supported local image imports, EXIF fallback, clinical metadata, worklist
  copying, stable identity, serialization, and separate compressed preservation.
- Test the three capabilities through thin adapters and independently validate output.
- Publish a capability matrix distinguishing encoding, decoding, and preservation.
- Run available Apple/Python checks; do not call simulator cross-builds simulator tests.
- Add CI/release guidance and request PR review. Keep #82 open for any unmet criteria.

## Environmental limit

mainframe1 is reachable as the separately provisioned `amagni-agent` build user.
Xcode 26.3 cannot resolve a tools-6.4 package for simulator testing. Continue using
isolated Swift 6.4.1 and available SDKs without upgrading host software. No Linux
qualification, complete profile conformance, or iOS simulator execution is implied.
