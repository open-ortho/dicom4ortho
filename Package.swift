// swift-tools-version: 6.4
// SwiftPM resolves Git-URL packages from a root manifest. Python packaging stays
// at the root unchanged; all Swift implementation files belong under apple/.
import PackageDescription

let package = Package(
    name: "DICOM4Ortho",
    platforms: [.iOS(.v18), .macOS(.v15)],
    products: [.library(name: "DICOM4Ortho", targets: ["DICOM4Ortho"])],
    dependencies: [
        .package(url: "https://github.com/raster-labs/DICOMKit.git", exact: "2.7.0")
    ],
    targets: [
        .target(
            name: "DICOM4Ortho",
            dependencies: [.product(name: "DICOMKit", package: "DICOMKit")],
            path: "apple/Sources/DICOM4Ortho"
        ),
        .testTarget(
            name: "DICOM4OrthoTests",
            dependencies: ["DICOM4Ortho", .product(name: "DICOMKit", package: "DICOMKit")],
            path: "apple/Tests/DICOM4OrthoTests"
        )
    ],
    swiftLanguageModes: [.v6]
)
