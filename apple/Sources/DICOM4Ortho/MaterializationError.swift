// Defines failures owned by the orthodontic layer. Dependency and filesystem
// errors retain their original types so callers can diagnose their actual source.

/// Input or clinical-profile errors, distinct from DICOMKit and file-access errors.
public enum MaterializationError: Error, Equatable, Sendable {
    /// API-only checkpoint: this operation has no implementation yet.
    case notImplemented(String)
    /// The normalized photograph keyword is absent from the bundled catalog.
    case unknownImageType(String)
    /// A complete image needs an explicit direction for this variable-direction view.
    case directionRequired(String)
    /// The requested keyword is not a supported projection direction.
    case unknownDirection(String)
    /// Dimensions, precision, or sample byte count are invalid or unsupported.
    case invalidPixelData
    /// A UID is malformed or reused across study, series, and instance levels.
    case invalidUID(String)
    /// A required code or mapping is missing from the bundled resource.
    case invalidTerminology(String)
    /// Lossy quality must be finite and strictly between zero and one.
    case invalidCompressionQuality
    /// The treatment event is not a valid Gregorian calendar date.
    case invalidClinicalDate
    /// Treatment progress requires an actual acquisition date.
    case acquisitionDateRequired
    /// The treatment event occurs after acquisition.
    case treatmentEventAfterAcquisition
    /// The image container, compressed process, or pixel layout is unsupported.
    case unsupportedImage
    /// The supplied worklist has no scheduled step at the requested zero-based index.
    case invalidScheduledStep(Int)
    /// A known clinical field violates its DICOM value representation.
    case invalidMetadata(String)
}
