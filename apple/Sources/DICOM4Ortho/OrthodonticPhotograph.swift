// Defines the image lifecycle and the three shared functional capabilities. Clinical
// mapping and codecs belong in implementation files, not application/test adapters.
import Foundation
import DICOMCore
import DICOMKit

/// A materialized still photograph with value semantics. Construction does not save a file.
public struct OrthodonticPhotograph: Sendable {
    /// Dependency-native dataset for inspection and advanced edits. The caller is
    /// responsible for consistency after raw edits; edits do not remap the profile.
    public var dataSet: DataSet
    /// Actual output representation. Serialization does not recompress pixels.
    public let transferSyntax: TransferSyntax

    /// Creates one VL Photographic image from supplied evidence and clinical metadata.
    /// Encoded-source preservation and pixel encoding are separate policies; unsupported
    /// combinations throw. No network operation occurs.
    public init(
        image: PhotographInput, metadata: PhotographMetadata,
        encoding: PhotographEncoding = .preserveSource
    ) throws {
        let file: DICOMFile
        switch image {
        case .rgb8(let data, let width, let height):
            file = try PixelMaterialization.rgb8(data, width: width, height: height,
                                                metadata: metadata, encoding: encoding)
        case .encoded(let data):
            file = try ImageImport.materialize(data, metadata: metadata, encoding: encoding)
        case .file(let url):
            guard url.isFileURL else { throw CocoaError(.fileReadUnsupportedScheme) }
            file = try ImageImport.materialize(Data(contentsOf: url), metadata: metadata, encoding: encoding)
        }
        guard let uid = file.transferSyntaxUID, let syntax = TransferSyntax.from(uid: uid) else {
            throw MaterializationError.unsupportedImage
        }
        dataSet = file.dataSet
        transferSyntax = syntax
    }

    /// Creates a view-populated template with no Pixel Data, image dimensions, patient
    /// facts, acquisition time, or allocated instance identity. A variable direction
    /// may remain absent. This is not necessarily an exchange-ready DICOM instance.
    public static func createStub(view: String, directionKeyword: String? = nil) throws -> DataSet {
        try PhotographProfile().makeStub(view: view, directionKeyword: directionKeyword, complete: false)
    }

    /// Lists bundled photograph types in keyword order without live terminology access.
    public static func availableViews() throws -> [PhotographView] {
        try Terminology.bundled().imageTypes.values.sorted { $0.keyword < $1.keyword }.map {
            PhotographView(keyword: $0.keyword, abbreviation: $0.abbreviation,
                           meaning: $0.meaning, code: $0.code.dataSet)
        }
    }

    /// Reads Request Attributes protocol codes (DENT-OIP #12), legacy/private
    /// VL image View Code Sequence declarations, and every worklist scheduled
    /// step/protocol item, and copied Request Attributes protocol items. Returns a
    /// collection even for one/zero results; preserves sequence order and repetitions.
    /// Coded matching uses identity, never Code Meaning, Image Comments or anatomy. Unrelated
    /// projection/procedure codes and incomplete coded entries are not type declarations.
    /// Qualifying unknown private codes have a nil keyword. Input is not mutated and
    /// pixels are not decoded. Other IOD-specific locations are not exhaustively searched.
    /// Request protocol lists describe prescriptions, not necessarily this instance's
    /// actual view. No implicit Instance Number to protocol-index mapping is performed.
    public static func extractViews(from dataSet: DataSet) throws -> [DeclaredView] {
        try ViewExtraction.extract(dataSet)
    }

    /// Serializes Part 10 bytes, regenerating File Meta Information from the current
    /// dataset. Valid identities are retained; malformed or colliding UIDs throw.
    /// This checks managed invariants, not complete DICOM/DENT-OIP conformance.
    public func dicomData() throws -> Data {
        try MetadataValidation.identities(dataSet)
        return try DICOMFile.create(dataSet: dataSet, transferSyntaxUID: transferSyntax.uid).write()
    }

    /// Writes Part 10 bytes atomically to a local URL. Parent directories must exist.
    /// This is the only output filesystem operation; remote URLs are rejected.
    public func save(to url: URL) throws {
        guard url.isFileURL else { throw CocoaError(.fileWriteUnsupportedScheme) }
        try dicomData().write(to: url, options: .atomic)
    }
}
