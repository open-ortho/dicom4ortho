# Swift qualification record

This file distinguishes observed results from implementation intent. A passing
validator or codec test is not a declaration of full DENT-OIP/clinical conformance.
The shared GXV/reference suite described in `docs/API_CONTRACT.md` is not available yet.

## Recorded environment

- mainframe1: Apple Silicon, macOS 15.8.1, Xcode 26.3 (17C529), installed iOS SDK 26.2.
- Isolated official Swift 6.4.1 toolchain; Swift 6 language mode; iOS deployment target 18.
- DICOMKit 2.7.0 plus exact observed revisions in root `Package.resolved`.
- An independent consumer package resolves the public fork's API branch and compiles;
  the implementation branch also resolves by Git URL and creates/serializes/extracts
  EV01 through public declarations without access to internal implementation types.
- No changes to the build host's OS, Xcode selection/installation, or security settings.
- Linux support is not claimed. Python is used only by independent validation/tooling.

## Observed checks (2026-10-21)

- Twenty-one Swift tests cover public API, templates, all 73 view mappings, extraction, worklist copying,
  clinical dates/personnel/identity, input imports, save lifecycle, and codec tests pass.
- All 13 output policies independently decode at 64×64 synthetic RGB after the
  request-code correction. Earlier codec checks also decoded 1024×1024 and 2048×2048;
  those larger checks predate the metadata-location correction.
  Lossless paths reproduce the source samples exactly; lossy errors are measured,
  not interpreted as clinical-quality acceptance thresholds.
- Independent decoders: pydicom 3 with libjpeg/OpenJPEG/CharLS plugins, Pillow's JPEG
  decoder, and libjxl 0.12.0 `djxl`. DICOMKit self-readback is not this oracle.
- Independent `dciodvfy` snapshot 20260927113651 checks all 90 corrected encoding/view/
  clinical/worklist/multi-request instances without errors. Empty Type 2 DICOMDIR fields and the
  validator's standard-extended profile warnings remain; neither is hidden.
- Python: 141 non-E2E tests pass, four skips. The maintainer-authorized code-location
  correction changes Python runtime behavior; terminology lock and packaging remain
  unchanged. Generator changes have offline parity/drift tests;
  error-only Pylint and Python wheel/source-archive builds also pass.
- iOS device and simulator library cross-builds pass on the recorded SDK/toolchain.
  These are compile checks, **not test execution on either device or simulator**.

## Codec capabilities

Encoding means accepting interleaved RGB8 and producing a new compressed stream.
Independent decoding below means the **output was decoded by external tools**;
it does not mean DICOM4Ortho exposes a generic DICOM pixel decoder.

| Output policy | RGB8 encoding | Independent output decoding | Existing-source preservation |
| --- | --- | --- | --- |
| Explicit / Implicit VR Little Endian | Yes | Exact | Raw RGB remains uncompressed |
| JPEG Baseline | Yes, explicit quality | Measured lossy error | Supported 8-bit color baseline subset |
| JPEG Lossless SV1 | Yes | Exact | Not exposed for imported JPEG processes |
| JPEG-LS Lossless | Yes | Exact | Not exposed |
| JPEG 2000 lossless / lossy | Yes | Exact / measured | Supported JP2/J2K subset; explicit source history |
| HTJ2K lossless / RPCL / lossy | Yes | Exact / exact / measured | Supported raw subset with explicit source color/history |
| JPEG XL lossless / lossy | Yes | Exact / measured with libjxl | Not exposed |
| RLE Lossless | Yes | Exact | Not exposed |

Near-lossless JPEG-LS, JPEG Extended/Progressive preservation, JPEG 2000 Part 2,
JPEG XL reversible JPEG recompression, video, alpha, and higher precision are not
advertised as supported. In particular, DICOMKit refuses Part 2 encoding. Unsupported
policies/formats throw; they are not silently assigned a different transfer syntax.
The current tests are synthetic interoperability checks, not a production image corpus.

## Review corrections (2026-10-22)

- Current `develop` (the squash-merged API PR #85, `410f9d4`) is merged into the
  implementation branch. Conflict resolution retains real behavior, backend/resource
  dependencies and request-code corrections instead of restoring API placeholders.
- Python rejects orphan extension creators and incomplete declared extension contexts
  before changing the destination. Ordinary codes omit extension metadata. Its 143
  non-E2E tests pass with four skips, and error-only production/new-test Pylint passes.
  Four independently exported ordinary/valid-extension/rejected-input control cases
  pass `dciodvfy` without errors.
- EXIF content timestamps are converted to the fixed UTC offset emitted at acquisition,
  rather than a regional timezone's offset at digitization/editing. Content-only EXIF
  retains its known offset without fabricating acquisition fields. Explicit content
  values are unchanged. Spring/autumn DST and content-only regressions exercise both
  preserved JPEG and decoded output; independent Python checks reconstruct their UTC
  instants from serialized Content Date/Time and Timezone Offset From UTC.
- The resolved/fixed tree passes 24 Swift tests, both iOS library cross-builds and
  independent output decoding/mapping/UTC-instant checks. All 97 regenerated Swift
  instances pass `dciodvfy` without errors (the four Python creator cases above are
  separate). The new timestamp regressions were observed failing before the fix.
- These checks do not qualify actual iOS simulator test execution; the blocker below
  remains. The new revision must pass its own hosted CI run.

## Reproducing checks

On an Apple build host with compatible Swift and SDKs, from the repository root:

```sh
DICOM4ORTHO_TEST_ARTIFACTS=/path/to/synthetic-artifacts swift test --jobs 4
DICOM4ORTHO_TEST_IMAGE_SIZE=1024 DICOM4ORTHO_TEST_ARTIFACTS=/path/to/synthetic-artifacts swift test --jobs 4
DICOM4ORTHO_TEST_IMAGE_SIZE=2048 DICOM4ORTHO_TEST_ARTIFACTS=/path/to/synthetic-artifacts swift test --jobs 4
swift build --target DICOM4Ortho --triple arm64-apple-ios18.0 --sdk "$(xcrun --sdk iphoneos --show-sdk-path)" --scratch-path .build-ios-device --jobs 4
swift build --target DICOM4Ortho --triple arm64-apple-ios18.0-simulator --sdk "$(xcrun --sdk iphonesimulator --show-sdk-path)" --scratch-path .build-ios-simulator --jobs 4
```

In a separate validation environment, install the dependencies listed in
`apple/Tools/validate_outputs.py`, put `djxl` on PATH, and run:

```sh
PYTHONPATH=python python apple/Tools/validate_outputs.py /path/to/synthetic-artifacts --compare-python
find /path/to/synthetic-artifacts -name '*.dcm' -exec dciodvfy {} \;
```

`ContractTests.swift` contains thin adapters that call the actual public functions.
They do not implement clinical mappings or extraction. The Python comparison has
two deliberate label/orientation differences: a three-field human-readable Image
Comments label and empty Patient Orientation for IV28/IV30 rather than Python's
Type 2C omission. Both implementations now write the same coded Request Attributes /
Scheduled Protocol Code Sequence and keep one projection. Comments do not identify a view.

## Request-code correction

Following the maintainer's instruction and DENT-OIP #12, new codes use Request
Attributes / Scheduled Protocol Code Sequence instead of private projection extensions
or comment extraction. Current source/nightly §3.4.1.3 contains the instruction;
the old `latest` tag inspected earlier predates it. The correction preserves supplied
series/worklist request lists, repetitions, identifiers and code metadata. It does
not claim a unique instance association for a multi-view prescription; #25 remains open.
See [migration behavior](../docs/VIEW_CODE_LOCATION.md) for Python's scalar convenience
and explicit-index updates. Validation results for the earlier representation are
historical, not proof of the new output. The corrected outputs are re-exported and
independently checked, including both languages' exact request-code locations,
projection cardinality, repeated protocols and separate request identifiers.

## Remaining acceptance limits

1. **iOS simulator test execution remains blocked** by Xcode 26.3's resolver rejecting
   a Swift-tools-6.4 manifest. A compatible Xcode/host or suitable hosted runner is needed.
   Do not solve this by downgrading a manifest without qualifying its actual dependencies.
   A standalone simulator test-target build was also attempted: its Swift Testing
   macro expansion fails against the installed older SDK/testing support. Library
   cross-compilation remains successful; test-target compilation is not claimed.
2. A hosted CI run at `2a152a0` passed on macos-15 with the selected Xcode 26.3 SDKs:
   [run 39664887512](https://github.com/zgypa-agent/dicom4ortho/actions/runs/39664887512).
   Subsequent revisions must retain green CI; this earlier success is not evidence
   for a revision it did not test. The setup-swift v2 action did not list 6.4.1. CI extracts the exact official
   package using its qualified SHA-256 and trusted signature instead of changing a
   package manifest to accommodate an older compiler.
3. Shared DENT-OIP/GXV conformance is not established; expand the reference corpus as it arrives.
4. No release tag has been published. Use the checklist before claiming a distributable release.

#82 must remain open while a required acceptance check is unmet. These limits do not
turn the API into a Python-cloning mandate or authorize a backend/host-OS replacement.
