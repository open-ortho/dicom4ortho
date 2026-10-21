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

// Library-owned registered UID and the CID extended by the DENT-OIP profile.
// Neither is an alternative DICOM transfer-syntax or SOP-class registry.
enum DentalProfile {
    static let creatorUID = "1.3.6.1.4.1.61741.11.2"
    static let viewContextIdentifier = "4063"
}

extension DataSet {
    var sequenceItem: SequenceItem { SequenceItem(elements: tags.compactMap { self[$0] }) }
}
