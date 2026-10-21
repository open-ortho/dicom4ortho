// Supplies dental concepts and identity to image creation. Advanced DICOM fields
// use the dependency dataset directly; this is not another generic dataset model.
import Foundation
import DICOMCore
import DICOMKit

/// Clinical context for one image. Empty strings represent unknown Type 2 values.
/// Explicit metadata overrides EXIF fallback. No patient or treatment fact is inferred.
public struct PhotographMetadata: Sendable {
    public var patientID = ""
    public var patientFamilyName = ""
    public var patientGivenName = ""
    /// DICOM DA (`YYYYMMDD`), or empty when unknown.
    public var patientBirthDate = ""
    /// M/F/O or Male/Female/Other, case-insensitive; other nonempty values are rejected.
    public var patientSex = ""
    /// Reuse across images in the same study, not as their SOP Instance UID.
    public var studyInstanceUID: String
    /// Reuse across images in the same series; must differ from the study UID.
    public var seriesInstanceUID: String
    /// Identity of this final instance, retained across repeated serialization.
    public var sopInstanceUID: String
    /// ADA photograph keyword, with or without a hyphen (for example EV01 / EV-01).
    public var imageType: String
    /// Projection keyword, required for variable-direction complete images.
    public var directionKeyword: String?
    /// Actual acquisition instant. Explicit values take precedence over EXIF.
    public var acquisitionDateTime: Date?
    /// Timezone used when an acquisition source has no UTC offset and for day arithmetic.
    public var acquisitionTimeZone: TimeZone = .current
    public var treatmentProgress: TreatmentProgress?
    /// Responsible dental provider maps to Physicians of Record, not Referring Physician.
    public var providerFamilyName = ""
    public var providerGivenName = ""
    /// Person acquiring the image maps to Operators' Name.
    public var operatorFamilyName = ""
    public var operatorGivenName = ""
    public var manufacturer = ""
    public var studyDescription = ""
    /// Nil retains the profile's description; a supplied value replaces it.
    public var seriesDescription: String?
    public var seriesNumber = 0
    public var instanceNumber = 0
    /// Supplementary fields copied before managed profile, identity, pixel, and typed
    /// clinical fields are written. Those managed fields cannot be overridden here.
    /// For advanced edits after creation, use OrthodonticPhotograph.dataSet.
    public var additionalAttributes = DataSet()

    /// Generates independent UIDs under dicom4ortho's registered roots using DICOMKit.
    /// Replace study/series values with shared values for related photographs.
    public init(imageType: String) {
        self.imageType = imageType
        studyInstanceUID = UIDGenerator(root: "1.3.6.1.4.1.61741.11.2.2").generate().value
        seriesInstanceUID = UIDGenerator(root: "1.3.6.1.4.1.61741.11.2.3").generate().value
        sopInstanceUID = UIDGenerator(root: "1.3.6.1.4.1.61741.11.2.4").generate().value
    }

    /// Copies supported patient, referring-physician, study, and request facts from
    /// an already supplied worklist. The selected step is explicit and zero-based.
    /// This operation overwrites corresponding fields with supplied nonempty facts;
    /// it does not change imageType, acquisition time, provider, operator, or SOP UID.
    /// No worklist server is contacted. Set subsequent explicit corrections afterward.
    public func applyingWorklist(_ worklist: DataSet, scheduledStepIndex: Int) throws -> Self {
        try WorklistMapping.apply(worklist, stepIndex: scheduledStepIndex, to: self)
    }
}
