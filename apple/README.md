# DICOM4Ortho for Swift

**API-only checkpoint for #82.** Clinical operations currently throw
`MaterializationError.notImplemented`; this package does not yet create clinical
output. Another application can compile against these declarations and provide its
own test doubles. Do not treat API compilation as implementation conformance.

## Contract and usage

The [shared functional contract](../docs/API_CONTRACT.md) defines capabilities,
not public signatures. Swift exposes DICOMKit `DataSet` directly, as Python exposes
pydicom datasets. There is no second generic dataset model.

```swift
import Foundation
import DICOM4Ortho

var metadata = PhotographMetadata(imageType: "EV01")
metadata.patientID = "synthetic-001"
metadata.patientFamilyName = "Example"
metadata.patientGivenName = "Alex"
let photo = try OrthodonticPhotograph(
    image: .rgb8(Data([255, 0, 0]), width: 1, height: 1), metadata: metadata,
    encoding: .jpeg2000Lossless)
let bytes = try photo.dicomData()
try photo.save(to: URL(fileURLWithPath: "example.dcm"))

let template = try OrthodonticPhotograph.createStub(view: "IV28")
let declarations = try OrthodonticPhotograph.extractViews(from: photo.dataSet)
let catalog = try OrthodonticPhotograph.availableViews()
```

These calls demonstrate the fixed interface; they throw until PR2 implements it.
Creation maps a supported view, validates supplied facts, and handles pixels;
templates intentionally omit pixels and may lack required exchange metadata.
Extraction accepts already parsed datasets, including supplied worklists. Results
retain actual-versus-prescribed roles, item indices, repetitions, and unresolved
qualifying codes. No operation infers a view from anatomy or performs a network query.

Photograph-type codes use `RequestAttributesSequence.ScheduledProtocolCodeSequence`,
as directed by [DENT-OIP #12](https://github.com/open-ortho/dent-oip/issues/12) and
[current §3.4.1.3](https://open-ortho.github.io/dent-oip/nightly/V1_Orthodontic_Imaging_Profile/03_oip_process_flow/index.html#image-views-request-procedure-codes).
`DeclaredView.Source.requested` labels these as prescriptions, not acquired views.
Supplied series/worklist protocol lists must be retained; they do not uniquely identify
an instance. No implicit Instance Number to protocol-index mapping is promised.
Image Comments is a human-readable label only, never a coded-extraction source.
Legacy/private View Code Sequence declarations retain their original code datasets.
New output keeps the projection as its single View Code Sequence item; the remaining
instance-level question is tracked in [DENT-OIP #25](https://github.com/open-ortho/dent-oip/issues/25).

`PhotographInput` accepts RGB8, encoded bytes, and local files. `preserveSource`
means no recompression, or uncompressed output for raw samples; it must reject
unsupported preservation paths. Explicit encoding allows decoding/re-encoding and
makes additional lossy intent visible. The implementation PR will record qualified
format/codec combinations; enum cases alone are not support claims.

Share study/series UIDs through `PhotographMetadata` for related images, while
keeping SOP Instance UIDs distinct. No study/series wrapper classes or Python-style
object hierarchy are required. The returned photograph is a value; advanced dataset
edits affect that value and do not automatically rebuild clinical mappings.

`applyingWorklist(_:scheduledStepIndex:)` copies a selected supplied step's context
locally. It is separate from `extractViews`, which reads every step's prescriptions.
Set explicit corrections after copying worklist facts. This is not network delivery.

## Building and consuming

Requires Swift tools 6.4, Swift 6 mode, iOS 18 or macOS 15, matching the selected
DICOMKit 2.7.0 candidate. The root `Package.swift` is the Git-URL entry point;
all Swift sources/tests live under `apple/`. Python packaging is unchanged.

```sh
swift test
```

For pre-release integration, depend on this API branch/revision. Do not select a
Python release tag that predates `Package.swift`. Once the implementation is
qualified, a versioned Git tag will identify a Swift-consumable release. No release
tag or simulator qualification is claimed by this interface PR.

Before this PR is merged, an application package can resolve the API from the
author's public fork (Swift tools 6.4+ is still required even for this API checkpoint):

```swift
// In the consuming Package.swift dependencies:
.package(url: "https://github.com/zgypa-agent/dicom4ortho.git",
         branch: "zgypa-agent/82-swift-api")
// In the consuming target dependencies:
.product(name: "DICOM4Ortho", package: "dicom4ortho")
```

After merge/release, use the upstream `open-ortho/dicom4ortho` URL with a qualified
revision/tag instead. Branch references are pre-release integration aids, not stable releases.

The development Mac currently has Xcode 26.3 plus an isolated official Swift 6.4.1
toolchain. Standalone SwiftPM testing/cross-compilation can use that toolchain, but
Xcode's older resolver prevents simulator test execution. Neither the OS nor Xcode
will be upgraded automatically. Compiler requirements affect the build host;
deployment targets determine the oldest supported iOS. See Apple's
[Xcode compatibility table](https://developer.apple.com/support/xcode/).

## Boundaries and licensing

DICOMKit owns serialization, constants, and codecs. DICOM4Ortho owns dental clinical
mapping and extraction. Public inputs/outputs may use dependency-native datasets;
UI/camera frameworks, Python runtime, DIMSE, STOW-RS, authentication, and delivery
queues are excluded. DICOM4Ortho and DICOMKit are MIT-licensed. Retain upstream
codec dependency notices when redistributing them.
