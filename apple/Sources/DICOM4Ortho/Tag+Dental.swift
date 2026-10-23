// Convenience members missing from DICOMCore 2.7.0, resolved through its sibling
// dictionary instead of copying tag numbers into a second standard registry.
import DICOMCore
import DICOMKit
import DICOMDictionary

extension Tag {
    // These keys are invariants of the pinned dependency's bundled dictionary,
    // verified by the contract tests. They do not depend on caller input or a server.
    static let deviceSequence = DataElementDictionary.lookup(keyword: "DeviceSequence")!.tag
    static let viewCodeSequence = DataElementDictionary.lookup(keyword: "ViewCodeSequence")!.tag
    static let viewModifierCodeSequence = DataElementDictionary.lookup(keyword: "ViewModifierCodeSequence")!.tag
    static let scheduledProcedureStepSequence = DataElementDictionary.lookup(keyword: "ScheduledProcedureStepSequence")!.tag
}

// Library identity, legacy read context, and the explicitly unassigned CP concept.
// No new DICOM tag is needed: the proposed concept uses Acquisition Context.
enum DentalProfile {
    static let creatorUID = "1.3.6.1.4.1.61741.11.2"
    static let viewContextIdentifier = "4063"
    // DENT-OIP #25 proposal, pending WG-22/DICOM approval. AAAAAAA is a CP
    // placeholder, not an assigned DCM concept; keep it separate from the lock.
    static let intendedViewConcept = Terminology.Code(
        value: "AAAAAAA", scheme: "DCM", meaning: "Intended orthodontic photographic view")
}

extension DataSet {
    var sequenceItem: SequenceItem { SequenceItem(elements: tags.compactMap { self[$0] }) }
}
