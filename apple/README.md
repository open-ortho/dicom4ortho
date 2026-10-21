# DICOM4Ortho for Swift

Swift implementation of the three [shared capabilities](../docs/API_CONTRACT.md),
without networking. The package is not release-qualified. See the
[qualification record and remaining limits](QUALIFICATION.md).

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
    encoding: .explicitLittleEndian)
let bytes = try photo.dicomData()
try photo.save(to: URL(fileURLWithPath: "example.dcm"))

let template = try OrthodonticPhotograph.createStub(view: "IV28")
let declarations = try OrthodonticPhotograph.extractViews(from: photo.dataSet)
let catalog = try OrthodonticPhotograph.availableViews()
```

Creation maps a supported view, validates supplied facts, and handles pixels;
templates intentionally omit pixels and may lack required exchange metadata.
Extraction accepts already parsed datasets, including supplied worklists. Results
retain actual-versus-prescribed roles, item indices, repetitions, and unresolved
qualifying codes. No operation infers a view from anatomy or performs a network query.

For newly created images, the explicit declaration is DENT-OIP's structured
`keyword^abbreviation^meaning` Image Comments format. It is not arbitrary comment
inference. `DeclaredView.Source.imageComments` retains that text; its `code` is the
exact matched catalog entry. Legacy/private sequence declarations retain their original
code dataset. View Code Sequence remains a single projection item: DICOM PS3.3
Table C.8-77 and DENT-OIP do not permit appending a second type-code item beside it.
The format is documented in DENT-OIP's
[Image Comments section](https://github.com/open-ortho/dent-oip/blob/latest/source/DICOM/VL_Photographic_Image/General_Image/0020_4000_image_comments.rst).
Arbitrary comments, legacy two-field comments, and unknown structured-comment types
are not resolved by inference. Coded extraction supports the bundled catalog scheme
and qualifying private CID extensions; it does not claim to resolve every SNOMED
procedure code or recursively search unrelated IODs. Incomplete code entries are
ignored without suppressing valid entries elsewhere.

`PhotographInput` accepts RGB8, encoded bytes, and local files. `preserveSource`
means no recompression, or uncompressed output for raw samples; it must reject
unsupported preservation paths. Explicit encoding allows decoding/re-encoding and
makes additional lossy intent visible. The [capability matrix](QUALIFICATION.md#codec-capabilities)
records qualified combinations; enum cases alone are not support claims.

PNG, supported lossless TIFF, BMP, and supported JPEG sources can be decoded through ImageIO with an
explicit output encoding. RGB8 output is intentional: the selected VL IOD requires
8-bit samples; 16-bit samples must not be silently relabeled or down-converted.
Multiple frames/pages, alpha, and nonidentity EXIF orientation are rejected.
Normalize those sources explicitly in the application before calling the library.
HEIF/GIF, JPEG-in-TIFF, and unknown TIFF compression schemes are not accepted merely
because ImageIO can decode them; their source-loss histories need separate qualification.

Baseline 8-bit three-component YCbCr JPEG with a JFIF or Adobe-transform-1 declaration
can be preserved without recompression. Headerless color assumptions and Adobe RGB/CMYK
JPEG are rejected. Explicit JPEG decoding accepts qualified 8-bit color baseline or
progressive processes, not an unqualified lossless process labeled as lossy.
JP2 preservation accepts a single sRGB codestream with three unsigned 8-bit components
and a supported MCT; palettes, channel mappings, Part 2 extensions, and coding-style
overrides are rejected. Raw J2K additionally needs an explicit RGB source declaration:

```swift
import DICOMCore
metadata.additionalAttributes.setString("RGB", for: .photometricInterpretation, vr: .CS)
metadata.additionalAttributes.setString("00", for: .lossyImageCompression, vr: .CS)
```

Only declare `00` if the source is known never to have undergone lossy compression.
Reversible wavelets do not prove absence of rate truncation or earlier loss. Unknown
JPEG 2000 history is rejected rather than guessed; irreversible streams cannot
declare `00`. Known earlier lossy history (`01`, with optional method/ratio) is retained
even when the requested output is lossless. Encapsulated streams receive only the
even-length padding required by DICOM; JP2 containers are not placed in Pixel Data.

EXIF DateTimeOriginal and camera Make are fallback facts. Explicit acquisition and
manufacturer values win. Acquisition timezone controls clinical day arithmetic;
editing time is never substituted for capture time. Treatment events after capture
are rejected; a zero-day offset is valid.
Camera model/software/serial and aperture/shutter values are copied only when the
corresponding supplementary attributes are absent. Digitization/editing timestamps
populate Content Date/Time, not Acquisition Date/Time; known source offsets are
converted to the dataset's selected timezone. Preservation is not de-identification:
the original compressed stream can still contain embedded EXIF information.

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

For pre-release integration, depend on the implementation branch/revision. Do not select a
Python release tag that predates `Package.swift`. Once the implementation is
qualified, a versioned Git tag will identify a Swift-consumable release. No release
tag or simulator test-execution qualification is claimed by this work.

Before merge, the implementation is available from the author's public fork:

```swift
// Consuming Package.swift dependencies:
.package(url: "https://github.com/zgypa-agent/dicom4ortho.git",
         branch: "zgypa-agent/82-swift-implementation")
// Consuming target dependencies:
.product(name: "DICOM4Ortho", package: "dicom4ortho")
```

After release, prefer the upstream `open-ortho/dicom4ortho` URL with a qualified tag.
Branch references are pre-release integration aids, not stable releases.

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
codec dependency notices when redistributing them. See [dependency notices](THIRD_PARTY.md)
and the [release checklist](RELEASING.md).
