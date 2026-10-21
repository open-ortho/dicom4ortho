// Reads explicit codes only. Scheduled protocols are prescriptions, never evidence
// that an image was acquired; scanning an unrelated coded sequence would hide that distinction.
import DICOMCore
import DICOMKit
import DICOMDictionary

enum ViewExtraction {
    static func extract(_ dataset: DataSet) throws -> [DeclaredView] {
        let terminology = try Terminology.bundled()
        var results: [DeclaredView] = []
        let sop = dataset.string(for: .sopClassUID)
        let imageSOP = UIDDictionary.lookup(keyword: "VLPhotographicImageStorage")?.uid
        if sop == nil || sop == imageSOP {
            for (index, item) in (dataset.sequence(for: .viewCodeSequence) ?? []).enumerated() {
                let code = DataSet(elements: item.allElements)
                if let occurrence = declaration(code, source: .image(viewCodeIndex: index),
                                                terminology: terminology, requireExtension: true) {
                    results.append(occurrence)
                }
            }
            if let text = dataset.string(for: .imageComments) {
                let parts = text.split(separator: "^", omittingEmptySubsequences: false).map(String.init)
                if parts.count == 3, let type = terminology.imageTypes[parts[0]],
                   parts[1] == type.abbreviation,
                   parts[2] == type.meaning.replacingOccurrences(of: "\u{a0}", with: " ") {
                    results.append(DeclaredView(keyword: type.keyword, code: type.code.dataSet,
                                                source: .imageComments(text)))
                }
            }
        }
        for (stepIndex, step) in (dataset.sequence(for: .scheduledProcedureStepSequence) ?? []).enumerated() {
            let step = DataSet(elements: step.allElements)
            for (codeIndex, item) in (step.sequence(for: .scheduledProtocolCodeSequence) ?? []).enumerated() {
                let source = DeclaredView.Source.scheduled(
                    stepIndex: stepIndex, protocolIndex: codeIndex,
                    stepID: step.string(for: .scheduledProcedureStepID))
                if let occurrence = declaration(DataSet(elements: item.allElements), source: source,
                                                terminology: terminology, requireExtension: false) {
                    results.append(occurrence)
                }
            }
        }
        for (requestIndex, request) in (dataset.sequence(for: .requestAttributesSequence) ?? []).enumerated() {
            let request = DataSet(elements: request.allElements)
            for (codeIndex, item) in (request.sequence(for: .scheduledProtocolCodeSequence) ?? []).enumerated() {
                if let occurrence = declaration(DataSet(elements: item.allElements),
                    source: .requested(requestIndex: requestIndex, protocolIndex: codeIndex),
                    terminology: terminology, requireExtension: false) {
                    results.append(occurrence)
                }
            }
        }
        return results
    }

    private static func declaration(
        _ code: DataSet, source: DeclaredView.Source, terminology: Terminology,
        requireExtension: Bool
    ) -> DeclaredView? {
        let identities = [Tag.codeValue, .longCodeValue, .urnCodeValue].compactMap {
            code.string(for: $0).flatMap { $0.isEmpty ? nil : $0 }
        }
        let scheme = code.string(for: .codingSchemeDesignator) ?? ""
        guard identities.count == 1, let value = identities.first,
              !scheme.isEmpty || code[.urnCodeValue] != nil,
              let meaning = code.string(for: .codeMeaning), !meaning.isEmpty else { return nil }
        let extended = code.string(for: .contextIdentifier) == DentalProfile.viewContextIdentifier
            && code.string(for: .contextGroupExtensionFlag) == "Y"
        let type = terminology.imageTypes.values.first { $0.code.value == value && $0.code.scheme == scheme }
        let catalogScheme = terminology.imageTypes.values.contains { $0.code.scheme == scheme }
        guard requireExtension ? extended : (catalogScheme || extended) else { return nil }
        let creator = code.string(for: .contextGroupExtensionCreatorUID)
        let matchingCreator = creator == nil || creator == DentalProfile.creatorUID
        // The bundle has no version-specific aliases. Retain other explicit versions
        // as unresolved rather than silently claiming a match to an unversioned code.
        let unversioned = (code.string(for: .codingSchemeVersion) ?? "").isEmpty
        return DeclaredView(keyword: matchingCreator && unversioned ? type?.keyword : nil,
                            code: code, source: source)
    }
}
