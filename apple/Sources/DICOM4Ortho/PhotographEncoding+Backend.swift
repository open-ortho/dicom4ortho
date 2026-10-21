// Adapts typed output policy to the selected dependency's public encoder names.
// UID definitions and codec selection remain DICOMKit's responsibility.
import DICOMCore
import DICOMKit

extension PhotographEncoding {
    var codecName: String {
        switch self {
        case .preserveSource, .explicitLittleEndian: "explicit-le"
        case .implicitLittleEndian: "implicit-le"
        case .jpegBaseline: "jpeg-baseline"
        case .jpegLossless: "jpeg-lossless-sv1"
        case .jpegLSLossless: "jpeg-ls-lossless"
        case .jpeg2000Lossless: "jpeg2000-lossless-only"
        case .jpeg2000Lossy: "jpeg2000-lossy"
        case .htj2kLossless: "htj2k-lossless-only"
        case .htj2kLosslessRPCL: "htj2k-rpcl-lossless-only"
        case .htj2kLossy: "htj2k-lossy"
        case .jpegXLLossless: "jpeg-xl-lossless-only"
        case .jpegXLLossy: "jpeg-xl-lossy"
        case .rleLossless: "rle"
        }
    }

    var quality: Double? {
        switch self {
        case .jpegBaseline(let value), .jpeg2000Lossy(let value),
             .htj2kLossy(let value), .jpegXLLossy(let value): value
        default: nil
        }
    }
}
