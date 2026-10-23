// Exercises public application values independently of internal implementation types.
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

@Test func publicOperationsProduceRealResults() throws {
    let photo = try OrthodonticPhotograph(image: .rgb8(Data([0, 0, 0]), width: 1, height: 1),
                                         metadata: .init(imageType: "EV01"))
    let parsed = try DICOMFile.read(from: photo.dicomData())
    #expect(parsed.sopInstanceUID == photo.dataSet.string(for: .sopInstanceUID))
    #expect(try OrthodonticPhotograph.availableViews().count == 73)
    #expect(try OrthodonticPhotograph.extractViews(from: DataSet()).isEmpty)
    #expect(throws: MaterializationError.invalidScheduledStep(0)) {
        try PhotographMetadata(imageType: "EV01").applyingWorklist(DataSet(), scheduledStepIndex: 0)
    }
}
