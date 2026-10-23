// Reads instance-level intended views and separately labeled protocol prescriptions.
// Neither clinical intention nor a prescription proves that a pose was achieved.
import DICOMCore
import DICOMKit
import DICOMDictionary

enum ViewExtraction {
    private enum Location { case intended, legacyImage, prescription }

    static func extract(_ dataset: DataSet) throws -> [DeclaredView] {
        let terminology = try Terminology.bundled()
        var results: [DeclaredView] = []
        let sop = dataset.string(for: .sopClassUID)
        let imageSOP = UIDDictionary.lookup(keyword: "VLPhotographicImageStorage")?.uid
        if sop == nil || sop == imageSOP {
            for (index, item) in (dataset.sequence(for: .acquisitionContextSequence) ?? []).enumerated() {
                let context = DataSet(elements: item.allElements)
                guard context.string(for: .valueType) == "CODE",
                      let names = context.sequence(for: .conceptNameCodeSequence), names.count == 1,
                      let values = context.sequence(for: .conceptCodeSequence), values.count == 1,
                      let name = identity(DataSet(elements: names[0].allElements)),
                      name.value == DentalProfile.intendedViewConcept.value,
                      name.scheme == DentalProfile.intendedViewConcept.scheme else { continue }
                if let occurrence = declaration(DataSet(elements: values[0].allElements),
                    source: .intended(acquisitionContextIndex: index), terminology: terminology,
                    location: .intended) {
                    results.append(occurrence)
                }
            }
            for (index, item) in (dataset.sequence(for: .viewCodeSequence) ?? []).enumerated() {
                let code = DataSet(elements: item.allElements)
                if let occurrence = declaration(code, source: .image(viewCodeIndex: index),
                                                terminology: terminology, location: .legacyImage) {
                    results.append(occurrence)
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
                                                 terminology: terminology, location: .prescription) {
                    results.append(occurrence)
                }
            }
        }
        for (requestIndex, request) in (dataset.sequence(for: .requestAttributesSequence) ?? []).enumerated() {
            let request = DataSet(elements: request.allElements)
            for (codeIndex, item) in (request.sequence(for: .scheduledProtocolCodeSequence) ?? []).enumerated() {
                if let occurrence = declaration(DataSet(elements: item.allElements),
                    source: .requested(requestIndex: requestIndex, protocolIndex: codeIndex),
                     terminology: terminology, location: .prescription) {
                    results.append(occurrence)
                }
            }
        }
        return results
    }

    private static func identity(_ code: DataSet) -> (value: String, scheme: String)? {
        let identities = [Tag.codeValue, .longCodeValue, .urnCodeValue].compactMap {
            code.string(for: $0).flatMap { $0.isEmpty ? nil : $0 }
        }
        let scheme = code.string(for: .codingSchemeDesignator) ?? ""
        guard identities.count == 1, let value = identities.first,
              !scheme.isEmpty || code[.urnCodeValue] != nil,
              let meaning = code.string(for: .codeMeaning), !meaning.isEmpty else { return nil }
        return (value, scheme)
    }

    private static func declaration(
        _ code: DataSet, source: DeclaredView.Source, terminology: Terminology, location: Location
    ) -> DeclaredView? {
        guard let (value, scheme) = identity(code) else { return nil }
        let extended = code.string(for: .contextIdentifier) == DentalProfile.viewContextIdentifier
            && code.string(for: .contextGroupExtensionFlag) == "Y"
        let type = terminology.imageTypes.values.first { $0.code.value == value && $0.code.scheme == scheme }
        // Older dicom4ortho worklists used 99OPOR. Preserve those occurrences,
        // unresolved: the bundle does not assert that private scheme's aliases.
        let catalogScheme = scheme == "99OPOR"
            || terminology.imageTypes.values.contains { $0.code.scheme == scheme }
        switch location {
        case .intended: break  // The exact concept identifies intent, even for an unknown value code.
        case .legacyImage: guard extended else { return nil }
        case .prescription: guard catalogScheme || extended else { return nil }
        }
        let creator = code.string(for: .contextGroupExtensionCreatorUID)
        let matchingCreator = extended ? creator == DentalProfile.creatorUID
            : (creator == nil || creator == DentalProfile.creatorUID)
        // The bundle has no version-specific aliases. Retain other explicit versions
        // as unresolved rather than silently claiming a match to an unversioned code.
        let unversioned = (code.string(for: .codingSchemeVersion) ?? "").isEmpty
        return DeclaredView(keyword: matchingCreator && unversioned ? type?.keyword : nil,
                            code: code, source: source)
    }
}
