// Thin adapters call the real public implementation. They normalize test plumbing
// only; view mapping/extraction and clinical defaults must never be implemented here.
import Foundation
import Testing
import DICOMCore
import DICOMKit
@testable import DICOM4Ortho

private enum ContractAdapter {
    static func create(_ keyword: String, metadata supplied: PhotographMetadata? = nil) throws -> OrthodonticPhotograph {
        var metadata = supplied ?? PhotographMetadata(imageType: keyword)
        if ["IV28", "IV30", "EV40"].contains(keyword) { metadata.directionKeyword = "projection_right" }
        return try OrthodonticPhotograph(image: .rgb8(Data([255, 0, 0]), width: 1, height: 1), metadata: metadata)
    }
    static func stub(_ keyword: String) throws -> DataSet {
        try OrthodonticPhotograph.createStub(view: keyword)
    }
    static func extract(_ dataset: DataSet) throws -> [DeclaredView] {
        try OrthodonticPhotograph.extractViews(from: dataset)
    }
}

@Test func allViewsCreateTemplatesAndExtractTheirExplicitDeclarations() throws {
    for view in try OrthodonticPhotograph.availableViews() {
        let stub = try ContractAdapter.stub(view.keyword)
        for tag in [Tag.pixelData, .rows, .columns, .patientID, .acquisitionDateTime, .sopInstanceUID,
                    .studyInstanceUID, .seriesInstanceUID] { #expect(stub[tag] == nil) }
        #expect((stub.sequence(for: .viewCodeSequence)?.count ?? 0) <= 1)
        #expect(try ContractAdapter.extract(stub).map(\.keyword) == [view.keyword])
        let photo = try ContractAdapter.create(view.keyword)
        let file = try DICOMFile.read(from: photo.dicomData())
        #expect(try ContractAdapter.extract(file.dataSet).map(\.keyword) == [view.keyword])
        #expect(file.dataSet.string(for: .patientOrientation) != nil)
        if let directory = ProcessInfo.processInfo.environment["DICOM4ORTHO_TEST_ARTIFACTS"] {
            let url = URL(fileURLWithPath: directory).appendingPathComponent("views", isDirectory: true)
            try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
            try photo.dicomData().write(to: url.appendingPathComponent(view.keyword + ".dcm"))
        }
    }
}

@Test func templatesDoNotRequireMissingDirectionButCompleteImagesDo() throws {
    #expect(try ContractAdapter.extract(ContractAdapter.stub("IV28")).first?.keyword == "IV28")
    #expect(throws: MaterializationError.directionRequired("IV28")) {
        try OrthodonticPhotograph(image: .rgb8(Data([0, 0, 0]), width: 1, height: 1),
                                  metadata: .init(imageType: "IV28"))
    }
    #expect(throws: MaterializationError.unknownImageType("unknown")) { try ContractAdapter.stub("unknown") }
    #expect(throws: MaterializationError.unknownDirection("Mouth")) {
        try OrthodonticPhotograph.createStub(view: "EV01", directionKeyword: "Mouth")
    }
}

private func step(_ codes: [DataSet], id: String) -> SequenceItem {
    var step = DataSet()
    step.setString(id, for: .scheduledProcedureStepID, vr: .SH)
    step.setSequence(codes.map(\.sequenceItem), for: .scheduledProtocolCodeSequence)
    return step.sequenceItem
}

@Test func worklistExtractionVisitsEveryItemWithoutCollapsingRolesOrRepetitions() throws {
    let views = try OrthodonticPhotograph.availableViews()
    let first = views[0], second = views[1]
    var worklist = DataSet()
    var unrelated = first.code
    unrelated.setString("99UNRELATED", for: .codingSchemeDesignator, vr: .SH)
    var unknown = first.code
    unknown.setString("CUSTOM", for: .codeValue, vr: .SH)
    var malformed = first.code
    malformed[.codeValue] = nil
    worklist.setSequence([
        step([unrelated, first.code, first.code, malformed], id: "A"),
        step([second.code, unknown], id: "B")
    ], for: .scheduledProcedureStepSequence)
    let results = try ContractAdapter.extract(worklist)
    #expect(results.map(\.keyword) == [first.keyword, first.keyword, second.keyword, nil])
    #expect(results[0].source == .scheduled(stepIndex: 0, protocolIndex: 1, stepID: "A"))
    #expect(results[2].source == .scheduled(stepIndex: 1, protocolIndex: 0, stepID: "B"))
    #expect(worklist.sequence(for: .scheduledProcedureStepSequence)?.count == 2)
    var mixed = try ContractAdapter.stub(first.keyword)
    mixed[.scheduledProcedureStepSequence] = worklist[.scheduledProcedureStepSequence]
    mixed.setSequence([step([second.code], id: "C")], for: .requestAttributesSequence)
    let mixedResults = try ContractAdapter.extract(mixed)
    #expect(mixedResults.count == 6)
    #expect(mixedResults.first?.source == .imageComments(mixed.string(for: .imageComments)!))
    #expect(mixedResults.last?.source == .requested(requestIndex: 0, protocolIndex: 0))
}

@Test func extractionNeverInfersViewsFromProjectionLabelsOrAnatomy() throws {
    var dataset = try ContractAdapter.stub("EV01")
    let items = dataset.sequence(for: .viewCodeSequence)!
    dataset[.imageComments] = nil
    dataset.setSequence([items[0]], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).isEmpty)
    var declaration = try OrthodonticPhotograph.availableViews()[0].code
    declaration.setString(DentalProfile.viewContextIdentifier, for: .contextIdentifier, vr: .CS)
    declaration.setString("Y", for: .contextGroupExtensionFlag, vr: .CS)
    declaration.setString("1.2.3.4", for: .contextGroupExtensionCreatorUID, vr: .UI)
    dataset.setSequence([declaration.sequenceItem], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).count == 1)
    #expect(try ContractAdapter.extract(dataset).first?.keyword == nil)
    declaration.setString(DentalProfile.creatorUID, for: .contextGroupExtensionCreatorUID, vr: .UI)
    declaration.setString("not-the-current-version", for: .codingSchemeVersion, vr: .SH)
    dataset.setSequence([declaration.sequenceItem], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).first?.keyword == nil)
}

@Test func structuredCommentsMustMatchTheEntireDeclaration() throws {
    var dataset = try ContractAdapter.stub("EV01")
    let declaration = dataset.string(for: .imageComments)!
    #expect(try ContractAdapter.extract(dataset).map(\.keyword) == ["EV01"])
    for text in ["EV01", "some text " + declaration, declaration + " extra text", "EV01^wrong^description"] {
        dataset.setString(text, for: .imageComments, vr: .LT)
        #expect(try ContractAdapter.extract(dataset).isEmpty)
    }
}

@Test func worklistCopyingUsesSelectedStepAndKeepsPersonnelRolesDistinct() throws {
    let view = try OrthodonticPhotograph.availableViews()[0]
    var worklist = DataSet()
    worklist.setString("Patient^Example", for: .patientName, vr: .PN)
    worklist.setString("new-id", for: .patientID, vr: .LO)
    worklist.setString("Referral^Doctor", for: .referringPhysicianName, vr: .PN)
    worklist.setSequence([step([view.code], id: "A"), step([view.code, view.code], id: "B")],
                         for: .scheduledProcedureStepSequence)
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.providerFamilyName = "Provider"
    metadata.operatorFamilyName = "Operator"
    let originalUID = metadata.sopInstanceUID
    metadata = try metadata.applyingWorklist(worklist, scheduledStepIndex: 1)
    let photo = try ContractAdapter.create("EV01", metadata: metadata)
    #expect(photo.dataSet.string(for: .patientID) == "new-id")
    #expect(photo.dataSet.string(for: .physiciansOfRecord) == "Provider^")
    #expect(photo.dataSet.string(for: .operatorsName) == "Operator^")
    #expect(photo.dataSet.string(for: .referringPhysicianName) == "Referral^Doctor")
    #expect(photo.dataSet.string(for: .sopInstanceUID) == originalUID)
    #expect(try ContractAdapter.extract(photo.dataSet).count == 3)
    try export(photo, name: "worklist")
    #expect(throws: MaterializationError.invalidScheduledStep(-1)) {
        try metadata.applyingWorklist(worklist, scheduledStepIndex: -1)
    }
}

@Test func identityAndClinicalTimeSurviveSerializationAndValueCopies() throws {
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.acquisitionTimeZone = TimeZone(secondsFromGMT: 0)!
    metadata.acquisitionDateTime = ISO8601DateFormatter().date(from: "2026-10-21T12:00:00Z")!
    metadata.treatmentProgress = .init(event: .patientRegistration,
                                      eventDate: try ClinicalDate(year: 2026, month: 10, day: 21))
    let first = try ContractAdapter.create("EV01", metadata: metadata)
    var second = first
    second.dataSet.setString("edited", for: .patientID, vr: .LO)
    #expect(first.dataSet.string(for: .patientID) == "")
    for _ in 0..<2 {
        let file = try DICOMFile.read(from: first.dicomData())
        #expect(file.sopInstanceUID == metadata.sopInstanceUID)
        #expect(file.dataSet.string(for: .acquisitionDate) == "20261021")
        #expect(file.dataSet.sequence(for: .acquisitionContextSequence)?.last?.string(for: .numericValue) == "0")
    }
    var siblingMetadata = metadata
    siblingMetadata.sopInstanceUID = PhotographMetadata(imageType: "EV01").sopInstanceUID
    let sibling = try ContractAdapter.create("EV01", metadata: siblingMetadata)
    #expect(sibling.dataSet.string(for: .studyInstanceUID) == first.dataSet.string(for: .studyInstanceUID))
    #expect(sibling.dataSet.string(for: .seriesInstanceUID) == first.dataSet.string(for: .seriesInstanceUID))
    #expect(sibling.dataSet.string(for: .sopInstanceUID) != first.dataSet.string(for: .sopInstanceUID))
    try export(first, name: "clinical-first")
    try export(sibling, name: "clinical-second")
    second.dataSet.setString("invalid", for: .sopInstanceUID, vr: .UI)
    #expect(throws: MaterializationError.invalidUID("invalid")) { try second.dicomData() }
}

private func export(_ photo: OrthodonticPhotograph, name: String) throws {
    guard let directory = ProcessInfo.processInfo.environment["DICOM4ORTHO_TEST_ARTIFACTS"] else { return }
    let url = URL(fileURLWithPath: directory, isDirectory: true)
    try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
    try photo.dicomData().write(to: url.appendingPathComponent(name + ".dcm"))
}

@Test func invalidClinicalValuesAndInputsThrowBeforeOutput() throws {
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.patientBirthDate = "20260230"
    #expect(throws: MaterializationError.self) { try ContractAdapter.create("EV01", metadata: metadata) }
    metadata.patientBirthDate = ""
    metadata.patientSex = "unknown-sex"
    #expect(throws: MaterializationError.self) { try ContractAdapter.create("EV01", metadata: metadata) }
    metadata.patientSex = ""
    metadata.treatmentProgress = .init(event: .patientRegistration,
                                      eventDate: try ClinicalDate(year: 2026, month: 10, day: 22))
    #expect(throws: MaterializationError.acquisitionDateRequired) {
        try ContractAdapter.create("EV01", metadata: metadata)
    }
    metadata.acquisitionDateTime = ISO8601DateFormatter().date(from: "2026-10-21T12:00:00Z")!
    #expect(throws: MaterializationError.treatmentEventAfterAcquisition) {
        try ContractAdapter.create("EV01", metadata: metadata)
    }
    #expect(throws: MaterializationError.invalidPixelData) {
        try OrthodonticPhotograph(image: .rgb8(Data([0]), width: Int.max, height: Int.max),
                                  metadata: .init(imageType: "EV01"))
    }
    #expect(throws: MaterializationError.invalidCompressionQuality) {
        try OrthodonticPhotograph(image: .rgb8(Data([0, 0, 0]), width: 1, height: 1),
                                  metadata: .init(imageType: "EV01"), encoding: .jpegBaseline(quality: .nan))
    }
}
