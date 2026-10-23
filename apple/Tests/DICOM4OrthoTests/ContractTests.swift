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
        #expect(stub[.requestAttributesSequence] == nil)
        #expect(stub[.performedProtocolCodeSequence] == nil)
        let intended = DataSet(elements: stub.sequence(for: .acquisitionContextSequence)![0].allElements)
        #expect(intended.string(for: .valueType) == "CODE")
        #expect(intended.sequence(for: .conceptNameCodeSequence)?.count == 1)
        #expect(intended.sequence(for: .conceptNameCodeSequence)?[0].string(for: .codeValue) == "AAAAAAA")
        #expect(intended.sequence(for: .conceptNameCodeSequence)?[0].string(for: .codingSchemeDesignator) == "DCM")
        #expect(intended.sequence(for: .conceptCodeSequence)?.count == 1)
        #expect(intended.sequence(for: .conceptCodeSequence)?[0].string(for: .codeValue) == view.keyword)
        #expect(try ContractAdapter.extract(stub).first?.source == .intended(acquisitionContextIndex: 0))
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
    mixed.setSequence([step([first.code, second.code], id: "C")], for: .requestAttributesSequence)
    let mixedResults = try ContractAdapter.extract(mixed)
    #expect(mixedResults.count == 7)
    #expect(mixedResults.first?.source == .intended(acquisitionContextIndex: 0))
    #expect(mixedResults[1].source == .scheduled(stepIndex: 0, protocolIndex: 1, stepID: "A"))
    #expect(mixedResults.last?.source == .requested(requestIndex: 0, protocolIndex: 1))
    var legacy = first.code
    legacy.setString("99OPOR", for: .codingSchemeDesignator, vr: .SH)
    worklist.setSequence([step([legacy], id: "legacy")], for: .scheduledProcedureStepSequence)
    let legacyResult = try ContractAdapter.extract(worklist)
    #expect(legacyResult.count == 1)
    #expect(legacyResult[0].keyword == nil)
    #expect(legacyResult[0].code.string(for: .codingSchemeDesignator) == "99OPOR")
}

@Test func extractionNeverInfersViewsFromProjectionLabelsOrAnatomy() throws {
    var dataset = try ContractAdapter.stub("EV01")
    let items = dataset.sequence(for: .viewCodeSequence)!
    dataset[.imageComments] = nil
    dataset[.requestAttributesSequence] = nil
    dataset.setSequence(Array(dataset.sequence(for: .acquisitionContextSequence)!.dropFirst()),
                        for: .acquisitionContextSequence)
    dataset.setSequence([items[0]], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).isEmpty)
    var declaration = try OrthodonticPhotograph.availableViews()[0].code
    declaration.setString(DentalProfile.viewContextIdentifier, for: .contextIdentifier, vr: .CS)
    declaration.setString("Y", for: .contextGroupExtensionFlag, vr: .CS)
    declaration.setString("1.2.3.4", for: .contextGroupExtensionCreatorUID, vr: .UI)
    dataset.setSequence([declaration.sequenceItem], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).count == 1)
    #expect(try ContractAdapter.extract(dataset).first?.source == .image(viewCodeIndex: 0))
    #expect(try ContractAdapter.extract(dataset).first?.keyword == nil)
    declaration.setString(DentalProfile.creatorUID, for: .contextGroupExtensionCreatorUID, vr: .UI)
    declaration.setString("not-the-current-version", for: .codingSchemeVersion, vr: .SH)
    dataset.setSequence([declaration.sequenceItem], for: .viewCodeSequence)
    #expect(try ContractAdapter.extract(dataset).first?.keyword == nil)
}

@Test func commentsAreNeverUsedInsteadOfCodedIntent() throws {
    var dataset = try ContractAdapter.stub("EV01")
    let declaration = dataset.string(for: .imageComments)!
    #expect(try ContractAdapter.extract(dataset).map(\.keyword) == ["EV01"])
    dataset[.requestAttributesSequence] = nil
    dataset.setSequence(Array(dataset.sequence(for: .acquisitionContextSequence)!.dropFirst()),
                        for: .acquisitionContextSequence)
    for text in [declaration, "EV01", "some text " + declaration, declaration + " extra text", "EV01^wrong^description"] {
        dataset.setString(text, for: .imageComments, vr: .LT)
        #expect(try ContractAdapter.extract(dataset).isEmpty)
    }
}

@Test func intendedViewExtractionRequiresTheProposedConceptAndKeepsUnknownOccurrences() throws {
    let stub = try ContractAdapter.stub("EV01")
    let original = DataSet(elements: stub.sequence(for: .acquisitionContextSequence)![0].allElements)
    let value = DataSet(elements: original.sequence(for: .conceptCodeSequence)![0].allElements)
    let name = DataSet(elements: original.sequence(for: .conceptNameCodeSequence)![0].allElements)
    var unknownValue = value
    unknownValue.setString("999999999", for: .codeValue, vr: .SH)
    unknownValue.setString("SCT", for: .codingSchemeDesignator, vr: .SH)
    unknownValue.setString("Unknown intended view", for: .codeMeaning, vr: .LO)
    unknownValue.setString("2026", for: .codingSchemeVersion, vr: .SH)
    var unknown = original
    unknown.setSequence([unknownValue.sequenceItem], for: .conceptCodeSequence)
    var unrelatedName = name
    unrelatedName.setString("128741", for: .codeValue, vr: .SH)
    var unrelated = original
    unrelated.setSequence([unrelatedName.sequenceItem], for: .conceptNameCodeSequence)
    var noName = original
    noName[.conceptNameCodeSequence] = nil
    var noMeaning = value
    noMeaning[.codeMeaning] = nil
    var incomplete = original
    incomplete.setSequence([noMeaning.sequenceItem], for: .conceptCodeSequence)
    var wrongType = original
    wrongType.setString("TEXT", for: .valueType, vr: .CS)
    var wrongSchemeName = name
    wrongSchemeName.setString("99UNRELATED", for: .codingSchemeDesignator, vr: .SH)
    var wrongScheme = original
    wrongScheme.setSequence([wrongSchemeName.sequenceItem], for: .conceptNameCodeSequence)
    var ambiguous = original
    ambiguous.setSequence([value.sequenceItem, value.sequenceItem], for: .conceptCodeSequence)
    // Code Meaning is descriptive, never the lookup key for either name or value.
    var alternateName = name
    alternateName.setString("Alternate display label", for: .codeMeaning, vr: .LO)
    var alternate = original
    alternate.setSequence([alternateName.sequenceItem], for: .conceptNameCodeSequence)
    var dataset = DataSet()
    dataset.setSequence([original, original, unknown, unrelated, noName, incomplete,
                         wrongType, wrongScheme, ambiguous, alternate].map(\.sequenceItem),
                        for: .acquisitionContextSequence)
    let results = try ContractAdapter.extract(dataset)
    #expect(results.map(\.keyword) == ["EV01", "EV01", nil, "EV01"])
    #expect(results.map(\.source) == [0, 1, 2, 9].map { DeclaredView.Source.intended(acquisitionContextIndex: $0) })
    #expect(results[2].code.string(for: .codingSchemeDesignator) == "SCT")
    #expect(results[2].code.string(for: .codingSchemeVersion) == "2026")
    #expect(dataset.sequence(for: .acquisitionContextSequence)?.count == 10)
}

@Test func creationKeepsInstanceIntentSeparateFromSeriesPrescriptions() throws {
    let views = try OrthodonticPhotograph.availableViews()
    var versioned = views[0].code
    versioned.setString("2026", for: .codingSchemeVersion, vr: .SH)
    var first = DataSet(elements: step([versioned, views[1].code, views[0].code], id: "A").allElements)
    first.setString("request-A", for: .requestedProcedureID, vr: .SH)
    first.setSequence([views[1].code.sequenceItem], for: .requestedProcedureCodeSequence)
    let second = step([views[1].code], id: "B")
    var metadata = PhotographMetadata(imageType: "IV01")
    metadata.instanceNumber = 999  // Never an implicit index into the protocol list.
    metadata.additionalAttributes.setSequence([first.sequenceItem, second], for: .requestAttributesSequence)
    let photo = try ContractAdapter.create("IV01", metadata: metadata)
    let stored = photo.dataSet.sequence(for: .requestAttributesSequence)!
    #expect(stored.count == 2)
    #expect(stored[0].string(for: .requestedProcedureID) == "request-A")
    let storedRequest = DataSet(elements: stored[0].allElements)
    #expect(storedRequest.sequence(for: .scheduledProtocolCodeSequence)?.count == 3)
    #expect(storedRequest.sequence(for: .scheduledProtocolCodeSequence)?[0]
        .string(for: .codingSchemeVersion) == "2026")
    #expect(storedRequest.sequence(for: .requestedProcedureCodeSequence)?.count == 1)
    let extracted = try ContractAdapter.extract(photo.dataSet)
    #expect(extracted.map(\.keyword) == ["IV01", nil, views[1].keyword, views[0].keyword, views[1].keyword])
    #expect(extracted.first?.source == .intended(acquisitionContextIndex: 0))
    #expect(extracted.last?.source == .requested(requestIndex: 1, protocolIndex: 0))
    #expect(photo.dataSet[.performedProtocolCodeSequence] == nil)
    #expect(photo.dataSet.sequence(for: .viewCodeSequence)?.count == 1)
    try export(photo, name: "series-requests")
    // Two different intended photograph types can share the exact same series request.
    var siblingMetadata = metadata
    siblingMetadata.imageType = "EV20"
    siblingMetadata.sopInstanceUID = PhotographMetadata(imageType: "EV20").sopInstanceUID
    let sibling = try ContractAdapter.create("EV20", metadata: siblingMetadata)
    #expect(sibling.dataSet.string(for: .seriesInstanceUID) == photo.dataSet.string(for: .seriesInstanceUID))
    #expect(sibling.dataSet.string(for: .sopInstanceUID) != photo.dataSet.string(for: .sopInstanceUID))
    #expect(try ContractAdapter.extract(sibling.dataSet).dropFirst().map(\.keyword)
        == extracted.dropFirst().map(\.keyword))
    #expect(try ContractAdapter.extract(sibling.dataSet).first?.keyword == "EV20")
    try export(sibling, name: "series-requests-sibling")
    var commentsEdited = photo.dataSet
    commentsEdited.setString("arbitrary note", for: .imageComments, vr: .LT)
    #expect(try ContractAdapter.extract(commentsEdited).map(\.keyword) == extracted.map(\.keyword))
    first[.scheduledProtocolCodeSequence] = nil
    metadata.additionalAttributes.setSequence([first.sequenceItem], for: .requestAttributesSequence)
    let emptyRequest = try ContractAdapter.create("IV01", metadata: metadata)
    #expect(try ContractAdapter.extract(emptyRequest.dataSet).map(\.keyword) == ["IV01"])
    #expect(emptyRequest.dataSet.sequence(for: .requestAttributesSequence)?[0]
        .string(for: .requestedProcedureID) == "request-A")
    #expect(DataSet(elements: emptyRequest.dataSet.sequence(for: .requestAttributesSequence)![0].allElements)
        .sequence(for: .scheduledProtocolCodeSequence) == nil)
    metadata.additionalAttributes.setSequence([first.sequenceItem, DataSet().sequenceItem],
                                               for: .requestAttributesSequence)
    #expect(try ContractAdapter.create("IV01", metadata: metadata)
        .dataSet.sequence(for: .requestAttributesSequence)?.count == 2)
}

@Test func worklistCopyingUsesSelectedStepAndKeepsPersonnelRolesDistinct() throws {
    let view = try OrthodonticPhotograph.availableViews()[0]
    var worklist = DataSet()
    worklist.setString("Patient^Example", for: .patientName, vr: .PN)
    worklist.setString("new-id", for: .patientID, vr: .LO)
    worklist.setString("WorklistAuthority", for: .issuerOfPatientID, vr: .LO)
    worklist.setString("Referral^Doctor", for: .referringPhysicianName, vr: .PN)
    worklist.setString("request-worklist", for: .requestedProcedureID, vr: .SH)
    worklist.setSequence([view.code.sequenceItem], for: .requestedProcedureCodeSequence)
    worklist.setSequence([step([view.code], id: "A"), step([view.code, view.code], id: "B")],
                         for: .scheduledProcedureStepSequence)
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.providerFamilyName = "Provider"
    metadata.operatorFamilyName = "Operator"
    let originalUID = metadata.sopInstanceUID
    metadata = try metadata.applyingWorklist(worklist, scheduledStepIndex: 1)
    let photo = try ContractAdapter.create("EV01", metadata: metadata)
    #expect(photo.dataSet.string(for: .patientID) == "new-id")
    #expect(photo.dataSet.string(for: .issuerOfPatientID) == "WorklistAuthority")
    #expect(photo.dataSet.string(for: .physiciansOfRecord) == "Provider^")
    #expect(photo.dataSet.string(for: .operatorsName) == "Operator^")
    #expect(photo.dataSet.string(for: .referringPhysicianName) == "Referral^Doctor")
    #expect(photo.dataSet.string(for: .sopInstanceUID) == originalUID)
    let request = DataSet(elements: photo.dataSet.sequence(for: .requestAttributesSequence)![0].allElements)
    #expect(request.sequence(for: .requestedProcedureCodeSequence)?.count == 1)
    #expect(try ContractAdapter.extract(photo.dataSet).count == 3)
    #expect(try ContractAdapter.extract(photo.dataSet).first?.source == .intended(acquisitionContextIndex: 0))
    try export(photo, name: "worklist")
    #expect(throws: MaterializationError.invalidScheduledStep(-1)) {
        try metadata.applyingWorklist(worklist, scheduledStepIndex: -1)
    }
    worklist.setString("Patient^Example^Middle^Dr.^III=例^示=れい^し", for: .patientName, vr: .PN)
    var full = try metadata.applyingWorklist(worklist, scheduledStepIndex: 0)
    full.patientGivenName = "Corrected"
    let fullName = try ContractAdapter.create("EV01", metadata: full)
    #expect(fullName.dataSet.string(for: .patientName) == "Patient^Corrected^Middle^Dr.^III=例^示=れい^し")
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
