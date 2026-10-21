// Validates library-managed inputs before they reach codecs. This is intentionally
// not a replacement for an independent IOD/profile validator or raw-dataset validation.
import Foundation
import DICOMCore
import DICOMKit

enum MetadataValidation {
    static let managedTags: [Tag] = [
        .pixelData, .rows, .columns, .samplesPerPixel, .planarConfiguration,
        .bitsAllocated, .bitsStored, .highBit, .pixelRepresentation, .photometricInterpretation,
        .lossyImageCompression, .lossyImageCompressionRatio, .lossyImageCompressionMethod,
        .sopClassUID, .sopInstanceUID, .studyInstanceUID, .seriesInstanceUID,
        .patientName, .patientID, .patientBirthDate, .patientSex, .acquisitionDateTime,
        .acquisitionDate, .acquisitionTime, .contentDate, .contentTime, .timezoneOffsetFromUTC,
        .viewCodeSequence, .anatomicRegionSequence, .primaryAnatomicStructureSequence,
        .deviceSequence, .acquisitionContextSequence, .imageType, .patientOrientation,
        .imageLaterality, .imageComments, .seriesDescription, .modality,
        .physiciansOfRecord, .operatorsName, .manufacturer, .studyDescription,
        .seriesNumber, .instanceNumber, .numberOfFrames
    ]

    static func identities(_ dataset: DataSet) throws {
        let values = [Tag.studyInstanceUID, .seriesInstanceUID, .sopInstanceUID].map {
            dataset.string(for: $0) ?? ""
        }
        for value in values where DICOMUniqueIdentifier.parse(value) == nil {
            throw MaterializationError.invalidUID(value)
        }
        guard Set(values).count == 3 else {
            throw MaterializationError.invalidUID("Study, series and instance UIDs must differ")
        }
    }

    static func validate(_ metadata: PhotographMetadata) throws {
        var identities = DataSet()
        identities.setString(metadata.studyInstanceUID, for: .studyInstanceUID, vr: .UI)
        identities.setString(metadata.seriesInstanceUID, for: .seriesInstanceUID, vr: .UI)
        identities.setString(metadata.sopInstanceUID, for: .sopInstanceUID, vr: .UI)
        try self.identities(identities)
        let names = [metadata.patientFamilyName, metadata.patientGivenName,
                     metadata.providerFamilyName, metadata.providerGivenName,
                     metadata.operatorFamilyName, metadata.operatorGivenName]
        for name in names {
            try text(name, maximum: 64)
            guard !name.contains("^") && !name.contains("=") else {
                throw MaterializationError.invalidMetadata("Name components must not contain ^ or =")
            }
        }
        for (family, given) in [(metadata.patientFamilyName, metadata.patientGivenName),
                                (metadata.providerFamilyName, metadata.providerGivenName),
                                (metadata.operatorFamilyName, metadata.operatorGivenName)] {
            try text(family + "^" + given, maximum: 64)
        }
        for value in [metadata.patientID, metadata.manufacturer, metadata.studyDescription,
                      metadata.seriesDescription ?? ""] { try text(value, maximum: 64) }
        if !metadata.patientBirthDate.isEmpty {
            guard metadata.patientBirthDate.utf8.count == 8,
                  metadata.patientBirthDate.utf8.allSatisfy({ (48...57).contains($0) }),
                  let date = DICOMDate.parse(metadata.patientBirthDate) else {
                throw MaterializationError.invalidMetadata("Patient Birth Date must be a valid DICOM DA")
            }
            // DICOMKit's DA parser accepts February 30; clinical inputs may not.
            _ = try ClinicalDate(year: date.year, month: date.month, day: date.day)
        }
        guard ["", "M", "F", "O", "MALE", "FEMALE", "OTHER"].contains(metadata.patientSex.uppercased()) else {
            throw MaterializationError.invalidMetadata("Patient Sex must be M, F, O, or empty")
        }
        for number in [metadata.seriesNumber, metadata.instanceNumber] where String(number).count > 12 {
            throw MaterializationError.invalidMetadata("DICOM IS values must fit within 12 characters")
        }
        if let acquisition = metadata.acquisitionDateTime {
            var calendar = Calendar(identifier: .gregorian)
            calendar.timeZone = metadata.acquisitionTimeZone
            guard acquisition.timeIntervalSince1970.isFinite,
                  (1...9999).contains(calendar.component(.year, from: acquisition)) else {
                throw MaterializationError.invalidMetadata("Acquisition timestamp is outside DICOM's date range")
            }
        }
    }

    private static func text(_ value: String, maximum: Int) throws {
        guard value.count <= maximum, !value.contains("\\"),
              !value.unicodeScalars.contains(where: { CharacterSet.controlCharacters.contains($0) }) else {
            throw MaterializationError.invalidMetadata("Text exceeds its VR limit or contains separators/control characters")
        }
    }
}
