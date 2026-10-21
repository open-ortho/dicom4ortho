// Keeps the clinical event distinct from the acquisition timestamp. Code identities
// come from the bundled terminology, not a second hand-maintained code registry.

/// Supported treatment events from the orthodontic profile.
public enum TreatmentEvent: String, Sendable, CaseIterable {
    case patientRegistration = "PatientRegistration"
    case orthodonticTreatmentStarted = "OrthodonticTreatmentStarted"
    case orthodonticTreatmentStopped = "OrthodonticTreatmentStopped"
}

/// The event and its actual calendar date; materialization calculates the day offset.
public struct TreatmentProgress: Sendable, Equatable {
    public let event: TreatmentEvent
    public let eventDate: ClinicalDate

    public init(event: TreatmentEvent, eventDate: ClinicalDate) {
        self.event = event
        self.eventDate = eventDate
    }
}
