// swift-tools-version: 6.4
// SwiftPM resolves Git-URL packages from a root manifest. Python packaging stays
// at the root unchanged; all Swift implementation files belong under apple/.
import PackageDescription

let package = Package(
    name: "DICOM4Ortho",
    platforms: [.iOS(.v18), .macOS(.v15)],
    products: [.library(name: "DICOM4Ortho", targets: ["DICOM4Ortho"])],
    dependencies: [
        .package(url: "https://github.com/raster-labs/DICOMKit.git", exact: "2.7.0"),
        // Already part of DICOMKit's graph. Use its public container/header readers
        // for compressed preservation instead of writing a duplicate JP2 box parser.
        .package(url: "https://github.com/Raster-Lab/J2KSwift.git", exact: "11.0.3")
    ],
    targets: [
        .target(
            name: "DICOM4Ortho",
            dependencies: [
                .product(name: "DICOMKit", package: "DICOMKit"),
                .product(name: "DICOMCore", package: "DICOMKit"),
                .product(name: "DICOMDictionary", package: "DICOMKit"),
                .product(name: "J2KCore", package: "J2KSwift"),
                .product(name: "J2KFileFormat", package: "J2KSwift")
            ],
            path: "apple/Sources/DICOM4Ortho",
            resources: [.process("Resources")]
        ),
        .testTarget(
            name: "DICOM4OrthoTests",
            dependencies: ["DICOM4Ortho", .product(name: "DICOMKit", package: "DICOMKit")],
            path: "apple/Tests/DICOM4OrthoTests"
        )
    ],
    swiftLanguageModes: [.v6]
)
