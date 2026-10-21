// Describes a bundled view for application selection without asking applications
// to parse the terminology resource or duplicate clinical labels.
import DICOMKit

/// One supported photograph type from the offline catalog.
public struct PhotographView: Sendable {
    public let keyword: String
    public let abbreviation: String
    public let meaning: String
    /// The original coded identity used for declaration and worklist matching.
    public let code: DataSet

    public init(keyword: String, abbreviation: String, meaning: String, code: DataSet) {
        self.keyword = keyword
        self.abbreviation = abbreviation
        self.meaning = meaning
        self.code = code
    }
}
