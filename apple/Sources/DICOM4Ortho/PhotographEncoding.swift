// Expresses loss intent separately from DICOMKit's transfer-syntax registry.
// Associated quality values are codec controls, not clinical-quality guarantees.
import DICOMCore

/// Output policy. Unsupported input/policy combinations throw rather than falling back.
public enum PhotographEncoding: Sendable, Equatable {
    /// Preserve supported compressed input without recompression; raw RGB uses explicit LE.
    /// An encoded format with no qualified preservation path is rejected, not transcoded.
    case preserveSource
    /// Uncompressed Explicit VR Little Endian.
    case explicitLittleEndian
    /// Uncompressed Implicit VR Little Endian.
    case implicitLittleEndian
    /// JPEG Baseline, with quality in the open interval (0, 1).
    case jpegBaseline(quality: Double)
    /// JPEG Lossless Process 14, Selection Value 1.
    case jpegLossless
    /// Reversible JPEG-LS.
    case jpegLSLossless
    /// JPEG 2000 lossless-only syntax.
    case jpeg2000Lossless
    /// Irreversible JPEG 2000, with quality in (0, 1).
    case jpeg2000Lossy(quality: Double)
    /// HTJ2K lossless-only syntax.
    case htj2kLossless
    /// HTJ2K lossless RPCL progressive profile.
    case htj2kLosslessRPCL
    /// Irreversible HTJ2K, with quality in (0, 1).
    case htj2kLossy(quality: Double)
    /// JPEG XL lossless-only syntax, not JPEG reversible recompression.
    case jpegXLLossless
    /// Irreversible JPEG XL, with quality in (0, 1).
    case jpegXLLossy(quality: Double)
    /// DICOM run-length encoding.
    case rleLossless
}
