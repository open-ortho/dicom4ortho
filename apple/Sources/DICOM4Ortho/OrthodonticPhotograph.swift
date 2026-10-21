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
    /// combinations throw. No network operation occurs. API-only checkpoint: always throws.
    public init(
        image: PhotographInput, metadata: PhotographMetadata,
        encoding: PhotographEncoding = .preserveSource
    ) throws {
        throw MaterializationError.notImplemented("create")
    }

    /// Creates a view-populated template with no Pixel Data, image dimensions, patient
    /// facts, acquisition time, or allocated instance identity. A variable direction
    /// may remain absent. This is not necessarily an exchange-ready DICOM instance.
    public static func createStub(view: String, directionKeyword: String? = nil) throws -> DataSet {
        throw MaterializationError.notImplemented("createStub")
    }

    /// Lists bundled photograph types in keyword order without live terminology access.
    public static func availableViews() throws -> [PhotographView] {
        throw MaterializationError.notImplemented("availableViews")
    }

    /// Reads explicit declarations from VL image View Code Sequence, every scheduled
    /// step/protocol item, and copied Request Attributes protocol items. Returns a
    /// collection even for one/zero results; preserves sequence order and repetitions.
    /// Catalog matching uses coded identity, never Code Meaning or anatomy. Unrelated
    /// projection/procedure codes and incomplete coded entries are not type declarations.
    /// Qualifying unknown private codes have a nil keyword. Input is not mutated and
    /// pixels are not decoded. Other IOD-specific locations are not exhaustively searched.
    public static func extractViews(from dataSet: DataSet) throws -> [DeclaredView] {
        throw MaterializationError.notImplemented("extractViews")
    }

    /// Serializes Part 10 bytes, regenerating File Meta Information from the current
    /// dataset. Valid identities are retained; malformed or colliding UIDs throw.
    /// This checks managed invariants, not complete DICOM/DENT-OIP conformance.
    public func dicomData() throws -> Data {
        throw MaterializationError.notImplemented("dicomData")
    }

    /// Writes Part 10 bytes atomically to a local URL. Parent directories must exist.
    /// This is the only output filesystem operation; remote URLs are rejected.
    public func save(to url: URL) throws {
        throw MaterializationError.notImplemented("save")
    }
}
