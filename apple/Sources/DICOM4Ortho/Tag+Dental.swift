// PS3.6 standard tags missing from DICOMKit 2.7.0's convenience members only.
// The upstream dictionary still owns these definitions; do not duplicate its other constants.
import DICOMCore
import DICOMKit

extension Tag {
    static let deviceSequence = Tag(group: 0x0050, element: 0x0010)
    static let viewCodeSequence = Tag(group: 0x0054, element: 0x0220)
    static let viewModifierCodeSequence = Tag(group: 0x0054, element: 0x0222)
    static let scheduledProcedureStepSequence = Tag(group: 0x0040, element: 0x0100)
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
