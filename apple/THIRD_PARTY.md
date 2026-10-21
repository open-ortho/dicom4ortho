# Dependency notices

The source graph qualified here is recorded in root `Package.resolved`. Versions
below identify observed upstream source licenses, not a blanket license for every
file or future dependency version. Retain upstream LICENSE/NOTICE material in any
redistribution that includes those components; review changes when updating the graph.

| Dependency | Version | Upstream license |
| --- | --- | --- |
| [DICOMKit](https://github.com/raster-labs/DICOMKit/tree/v2.7.0) | 2.7.0 | MIT |
| [J2KSwift](https://github.com/Raster-Lab/J2KSwift/tree/v11.0.3) | 11.0.3 | MIT |
| [JLISwift](https://github.com/raster-labs/JLISwift/tree/v0.6.0) | 0.6.0 | Apache-2.0 |
| [JLSwift](https://github.com/raster-labs/JLSwift/tree/v0.10.1) | 0.10.1 | Apache-2.0 |
| [JXLSwift](https://github.com/Raster-Lab/JXLSwift/tree/v1.4.0) | 1.4.0 | MIT |
| [CompressionFamily](https://github.com/Raster-Lab/CompressionFamily/tree/1.0.1) | 1.0.1 | Apache-2.0 |
| [swift-argument-parser](https://github.com/apple/swift-argument-parser/tree/1.8.2) | 1.8.2 | Apache-2.0 with Swift exception |

The library uses source packages, not a bundled native archive or XCFramework.
Its only product is DICOM4Ortho; no dependency network product is selected by the
library target. Dependency build internals do not add network delivery to this API.

Terminology is separately governed by its source terms, including applicable SNOMED CT
licensing. The committed bundle includes source provenance; MIT licensing of this
repository does not relicense third-party clinical terminology.
