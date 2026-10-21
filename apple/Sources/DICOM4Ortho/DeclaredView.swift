// Preserves the difference between an image declaration and an acquisition request.
// The original code dataset avoids losing private/unknown code context at the API boundary.
import DICOMKit

/// One explicit photograph-type occurrence, not a guess from anatomy or a filename.
public struct DeclaredView: Sendable {
    /// Resolved catalog keyword, or nil for a qualifying but unknown type code.
    public let keyword: String?
    /// Original coded entry, including scheme/version/extension metadata when present.
    public let code: DataSet
    public let source: Source

    /// Sequence association. Indices are zero-based and repeated declarations remain distinct.
    public enum Source: Sendable, Equatable {
        case image(viewCodeIndex: Int)
        case scheduled(stepIndex: Int, protocolIndex: Int, stepID: String?)
        case requested(requestIndex: Int, protocolIndex: Int)
    }

    public init(keyword: String?, code: DataSet, source: Source) {
        self.keyword = keyword
        self.code = code
        self.source = source
    }
}
