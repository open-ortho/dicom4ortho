// Copies an explicitly selected offline worklist context. This does not contact a
// server, select a step heuristically, or relabel a referring physician as the provider.
import DICOMCore
import DICOMKit

enum WorklistMapping {
    static func apply(_ worklist: DataSet, stepIndex: Int, to metadata: PhotographMetadata) throws -> PhotographMetadata {
        let steps = worklist.sequence(for: .scheduledProcedureStepSequence) ?? []
        guard steps.indices.contains(stepIndex) else {
            throw MaterializationError.invalidScheduledStep(stepIndex)
        }
        var result = metadata
        if let name = worklist.string(for: .patientName), !name.isEmpty,
           let parsed = DICOMPersonName.parse(name) {
            let groups = name.split(separator: "=", omittingEmptySubsequences: false)
            guard groups.count <= 3,
                  groups.allSatisfy({ $0.split(separator: "^", omittingEmptySubsequences: false).count <= 5 }) else {
                throw MaterializationError.invalidMetadata("Worklist Patient Name has invalid PN component cardinality")
            }
            result.worklistPatientName = parsed
            result.patientFamilyName = parsed.familyName
            result.patientGivenName = parsed.givenName
        }
        if let value = nonempty(worklist, .patientID) {
            result.patientID = value
            // An ID and its assigning authority travel together. Retaining the old
            // patient's issuer after replacing the ID would change its identity.
            for tag in [Tag.issuerOfPatientID, .issuerOfPatientIDQualifiersSequence] {
                result.additionalAttributes[tag] = worklist[tag]
            }
        }
        if let value = nonempty(worklist, .patientBirthDate) { result.patientBirthDate = value }
        if let value = nonempty(worklist, .patientSex) { result.patientSex = value }
        if let value = nonempty(worklist, .studyInstanceUID) { result.studyInstanceUID = value }
        if let value = nonempty(worklist, .studyDescription) { result.studyDescription = value }
        for tag in [Tag.referringPhysicianName, .accessionNumber, .studyID, .studyDate, .studyTime] {
            if nonempty(worklist, tag) != nil { result.additionalAttributes[tag] = worklist[tag] }
        }
        var request = DataSet(elements: steps[stepIndex].allElements)
        // Request Attributes carries scheduled/requested context, not actual image type.
        for tag in [Tag.accessionNumber, .requestedProcedureID, .requestedProcedureDescription] {
            if let value = worklist[tag] { request[tag] = value }
        }
        // Keep only attributes defined for the supported request context. A scheduled
        // station/time is not the image's acquisition station/time.
        let allowed: Set<Tag> = [.scheduledProcedureStepID, .scheduledProcedureStepDescription,
                                 .scheduledProtocolCodeSequence, .requestedProcedureID,
                                 .requestedProcedureDescription, .accessionNumber]
        request = DataSet(elements: request.tags.filter { allowed.contains($0) }.compactMap { request[$0] })
        result.additionalAttributes.setSequence([request.sequenceItem], for: .requestAttributesSequence)
        return result
    }

    private static func nonempty(_ dataset: DataSet, _ tag: Tag) -> String? {
        dataset.string(for: tag).flatMap { $0.isEmpty ? nil : $0 }
    }
}
