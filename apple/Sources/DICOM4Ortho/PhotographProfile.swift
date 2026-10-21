// Maps one known dental view to its DICOM sequences. Image-free templates and
// complete image creation share this mapper so clinical behavior cannot drift.
import Foundation
import DICOMCore
import DICOMKit
import DICOMDictionary

struct PhotographProfile {
    let terminology: Terminology

    init() throws { terminology = try .bundled() }

    func makeStub(view keyword: String, directionKeyword: String?, complete: Bool) throws -> DataSet {
        let keyword = keyword.replacingOccurrences(of: "-", with: "")
        guard let view = terminology.views[keyword], let type = terminology.imageTypes[keyword] else {
            throw MaterializationError.unknownImageType(keyword)
        }
        var direction = view.viewCode
        if let requested = directionKeyword {
            guard requested.hasPrefix("projection_"), let code = terminology.codes[requested] else {
                throw MaterializationError.unknownDirection(requested)
            }
            direction = code
        }
        if complete && direction == nil && keyword != "IV29" {
            throw MaterializationError.directionRequired(keyword)
        }
        var dataset = DataSet()
        dataset.setString("ISO_IR 192", for: .specificCharacterSet, vr: .CS)
        // Look up the standard SOP class rather than maintaining another UID literal.
        guard let sop = UIDDictionary.lookup(keyword: "VLPhotographicImageStorage") else {
            throw MaterializationError.invalidTerminology("VLPhotographicImageStorage")
        }
        dataset.setString(sop.uid, for: .sopClassUID, vr: .UI)
        dataset.setString("XC", for: .modality, vr: .CS)
        dataset.setString(view.seriesDescription, for: .seriesDescription, vr: .LO)
        // DENT-OIP explicitly defines this three-field declaration. It is not a
        // heuristic based on free-text comments or the projection/anatomy profile.
        dataset.setString("\(keyword)^\(type.abbreviation)^\(type.meaning)".replacingOccurrences(of: "\u{a0}", with: " "),
                          for: .imageComments, vr: .LT)
        dataset.setString(view.imageLaterality, for: .imageLaterality, vr: .CS)
        dataset.setStrings(view.patientOrientation ?? [], for: .patientOrientation, vr: .CS)
        dataset.setSequence([item(view.anatomicRegion, modifier: view.anatomicRegionModifier,
                                  modifierTag: .anatomicRegionModifierSequence)],
                            for: .anatomicRegionSequence)
        if let primary = view.primaryAnatomicStructure {
            dataset.setSequence([item(primary, modifier: view.primaryAnatomicStructureModifier,
                                      modifierTag: .primaryAnatomicStructureModifierSequence)],
                                for: .primaryAnatomicStructureSequence)
        }
        if !view.devices.isEmpty {
            dataset.setSequence(view.devices.map { $0.dataSet.sequenceItem }, for: .deviceSequence)
        }
        var viewItems: [SequenceItem] = []
        if let direction {
            var projection = direction.dataSet
            if !view.viewModifiers.isEmpty {
                projection.setSequence(view.viewModifiers.map { $0.dataSet.sequenceItem },
                                       for: .viewModifierCodeSequence)
            }
            viewItems.append(projection.sequenceItem)
        }
        // PS3.3 Table C.8-77 permits one View Code Sequence item. Do not append
        // an ADA type beside the projection as the older Python code helper can do.
        if !viewItems.isEmpty { dataset.setSequence(viewItems, for: .viewCodeSequence) }
        var context: [SequenceItem] = []
        let groups: [(String, [Terminology.Code])] = [
            ("OrthognathicFunctionalConditions", view.orthognathicFunctionalConditions),
            ("FindingByInspection", view.findingsByInspection),
            ("ObservableEntity", view.observableEntities),
            ("DentalOcclusion", view.dentalOcclusion.map { [$0] } ?? [])
        ]
        for (name, values) in groups {
            guard let concept = terminology.codes[name] else {
                throw MaterializationError.invalidTerminology(name)
            }
            for value in values {
                var element = DataSet()
                element.setString("CODE", for: .valueType, vr: .CS)
                element.setSequence([concept.dataSet.sequenceItem], for: .conceptNameCodeSequence)
                element.setSequence([value.dataSet.sequenceItem], for: .conceptCodeSequence)
                context.append(element.sequenceItem)
            }
        }
        dataset.setSequence(context, for: .acquisitionContextSequence)
        return dataset
    }

    func makeMetadata(_ metadata: PhotographMetadata) throws -> DataSet {
        try MetadataValidation.validate(metadata)
        var dataset = metadata.additionalAttributes
        for tag in dataset.tags where tag.group == 0x0002 { dataset[tag] = nil }
        // Supplementary attributes may not supply stale pixels, identities, profile
        // sequences or compression history from another image. Managed values follow.
        for tag in MetadataValidation.managedTags { dataset[tag] = nil }
        let profile = try makeStub(view: metadata.imageType,
                                   directionKeyword: metadata.directionKeyword, complete: true)
        for tag in profile.tags { dataset[tag] = profile[tag] }
        dataset.setString(metadata.sopInstanceUID, for: .sopInstanceUID, vr: .UI)
        dataset.setString(metadata.studyInstanceUID, for: .studyInstanceUID, vr: .UI)
        dataset.setString(metadata.seriesInstanceUID, for: .seriesInstanceUID, vr: .UI)
        dataset.setStrings(["ORIGINAL", "PRIMARY"], for: .imageType, vr: .CS)
        dataset.setString(metadata.patientID, for: .patientID, vr: .LO)
        dataset.setString(metadata.patientFamilyName + "^" + metadata.patientGivenName,
                          for: .patientName, vr: .PN)
        dataset.setString(metadata.patientBirthDate, for: .patientBirthDate, vr: .DA)
        let sexes = ["M": "M", "MALE": "M", "F": "F", "FEMALE": "F", "O": "O", "OTHER": "O"]
        dataset.setString(sexes[metadata.patientSex.uppercased()] ?? "", for: .patientSex, vr: .CS)
        for (family, given, tag) in [
            (metadata.providerFamilyName, metadata.providerGivenName, Tag.physiciansOfRecord),
            (metadata.operatorFamilyName, metadata.operatorGivenName, Tag.operatorsName)
        ] where !family.isEmpty || !given.isEmpty {
            dataset.setString(family + "^" + given, for: tag, vr: .PN)
        }
        for (tag, vr) in [(Tag.studyDate, VR.DA), (.studyTime, .TM), (.accessionNumber, .SH),
                          (.referringPhysicianName, .PN), (.studyID, .SH)] where dataset[tag] == nil {
            dataset.setString("", for: tag, vr: vr)
        }
        dataset.setString(String(metadata.seriesNumber), for: .seriesNumber, vr: .IS)
        dataset.setString(String(metadata.instanceNumber), for: .instanceNumber, vr: .IS)
        dataset.setString(metadata.manufacturer, for: .manufacturer, vr: .LO)
        if !metadata.studyDescription.isEmpty {
            dataset.setString(metadata.studyDescription, for: .studyDescription, vr: .LO)
        }
        if let description = metadata.seriesDescription {
            dataset.setString(description, for: .seriesDescription, vr: .LO)
        }
        for tag in [Tag.burnedInAnnotation, .qualityControlImage] where dataset[tag] == nil {
            dataset.setString("NO", for: tag, vr: .CS)
        }
        try applyClinicalMetadata(metadata, to: &dataset)
        return dataset
    }

    private func applyClinicalMetadata(_ metadata: PhotographMetadata, to dataset: inout DataSet) throws {
        if let acquired = metadata.acquisitionDateTime {
            let formatter = DateFormatter()
            formatter.locale = Locale(identifier: "en_US_POSIX")
            formatter.calendar = Calendar(identifier: .gregorian)
            formatter.timeZone = metadata.acquisitionTimeZone
            formatter.dateFormat = "yyyyMMdd"
            let date = formatter.string(from: acquired)
            formatter.dateFormat = "HHmmss.SSSSSS"
            let time = formatter.string(from: acquired)
            formatter.dateFormat = "Z"
            let offset = formatter.string(from: acquired)
            dataset.setString(date + time + offset, for: .acquisitionDateTime, vr: .DT)
            dataset.setString(date, for: .acquisitionDate, vr: .DA)
            dataset.setString(time, for: .acquisitionTime, vr: .TM)
            if dataset[.contentDate] == nil { dataset.setString(date, for: .contentDate, vr: .DA) }
            if dataset[.contentTime] == nil { dataset.setString(time, for: .contentTime, vr: .TM) }
            dataset.setString(offset, for: .timezoneOffsetFromUTC, vr: .SH)
        }
        guard let progress = metadata.treatmentProgress else { return }
        guard let acquired = metadata.acquisitionDateTime else {
            throw MaterializationError.acquisitionDateRequired
        }
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = metadata.acquisitionTimeZone
        let acquisitionDay = try ClinicalDate(year: calendar.component(.year, from: acquired),
                                              month: calendar.component(.month, from: acquired),
                                              day: calendar.component(.day, from: acquired))
        let days = try progress.eventDate.days(until: acquisitionDay)
        guard days >= 0 else { throw MaterializationError.treatmentEventAfterAcquisition }
        guard let eventCode = terminology.codes[progress.event.rawValue],
              let eventName = terminology.codes["TemporalEventType"],
              let offsetName = terminology.codes["OffsetFromEvent"],
              let dayCode = terminology.codes["day"] else {
            throw MaterializationError.invalidTerminology("Treatment progress")
        }
        var event = DataSet()
        event.setString("CODE", for: .valueType, vr: .CS)
        event.setSequence([eventName.dataSet.sequenceItem], for: .conceptNameCodeSequence)
        event.setSequence([eventCode.dataSet.sequenceItem], for: .conceptCodeSequence)
        var offset = DataSet()
        offset.setString("NUMERIC", for: .valueType, vr: .CS)
        offset.setSequence([offsetName.dataSet.sequenceItem], for: .conceptNameCodeSequence)
        offset.setSequence([dayCode.dataSet.sequenceItem], for: .measurementUnitsCodeSequence)
        offset.setString(String(days), for: .numericValue, vr: .DS)
        var context = dataset.sequence(for: .acquisitionContextSequence) ?? []
        context += [event.sequenceItem, offset.sequenceItem]
        dataset.setSequence(context, for: .acquisitionContextSequence)
    }

    private func item(_ code: Terminology.Code, modifier: Terminology.Code?, modifierTag: Tag) -> SequenceItem {
        var dataset = code.dataSet
        if let modifier { dataset.setSequence([modifier.dataSet.sequenceItem], for: modifierTag) }
        return dataset.sequenceItem
    }
}
