// Compiles the application-facing surface before implementation work begins.
// These tests deliberately do not pass off placeholder output as clinical behavior.
import Foundation
import Testing
import DICOMCore
import DICOMKit
import DICOM4Ortho

@Test func clinicalDatesRejectImpossibleValues() throws {
    let date = try ClinicalDate(year: 2024, month: 2, day: 29)
    #expect(date.day == 29)
    #expect(throws: MaterializationError.invalidClinicalDate) {
        try ClinicalDate(year: 2026, month: 2, day: 29)
    }
}

@Test func metadataAndDeclarationValuesAreUsableByApplications() throws {
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.patientID = "synthetic-001"
    metadata.treatmentProgress = TreatmentProgress(
        event: .patientRegistration, eventDate: try ClinicalDate(year: 2026, month: 1, day: 1))
    #expect(Set([metadata.studyInstanceUID, metadata.seriesInstanceUID,
                 metadata.sopInstanceUID]).count == 3)
    let occurrence = DeclaredView(keyword: nil, code: DataSet(),
                                 source: .scheduled(stepIndex: 1, protocolIndex: 2, stepID: "step-b"))
    #expect(occurrence.keyword == nil)
    #expect(occurrence.source == .scheduled(stepIndex: 1, protocolIndex: 2, stepID: "step-b"))
}

@Test func apiOnlyOperationsFailExplicitly() {
    #expect(throws: MaterializationError.notImplemented("create")) {
        try OrthodonticPhotograph(image: .rgb8(Data([0, 0, 0]), width: 1, height: 1),
                                  metadata: .init(imageType: "EV01"))
    }
    #expect(throws: MaterializationError.notImplemented("createStub")) {
        try OrthodonticPhotograph.createStub(view: "EV01")
    }
    #expect(throws: MaterializationError.notImplemented("extractViews")) {
        try OrthodonticPhotograph.extractViews(from: DataSet())
    }
    #expect(throws: MaterializationError.notImplemented("availableViews")) {
        try OrthodonticPhotograph.availableViews()
    }
    #expect(throws: MaterializationError.notImplemented("applyingWorklist")) {
        try PhotographMetadata(imageType: "EV01").applyingWorklist(DataSet(), scheduledStepIndex: 0)
    }
}
