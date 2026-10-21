// Copies qualified EXIF fallback facts without confusing acquisition, digitization,
// editing, or clinical treatment dates. Explicit application values take precedence.
import Foundation
import DICOMCore
import DICOMKit
import DICOMDictionary
#if canImport(ImageIO)
import ImageIO

enum EXIFMetadata {
    static func applying(_ properties: [String: Any], to metadata: PhotographMetadata) throws -> PhotographMetadata {
        var result = metadata
        let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any] ?? [:]
        let exif = properties[kCGImagePropertyExifDictionary as String] as? [String: Any] ?? [:]
        try copyEquipment(tiff: tiff, exif: exif, to: &result)
        if metadata.acquisitionDateTime == nil {
            if let offset = exif["OffsetTimeOriginal"] as? String {
                result.acquisitionTimeZone = try timeZone(offset)
            }
            if let date = exif[kCGImagePropertyExifDateTimeOriginal as String] as? String {
                result.acquisitionDateTime = try parse(date, timeZone: result.acquisitionTimeZone)
            }
        }
        // DICOM's dataset UTC offset applies to Content Date/Time too. Convert any
        // distinct EXIF digitization/editing offset into the selected output zone.
        if result.additionalAttributes[.contentDate] == nil && result.additionalAttributes[.contentTime] == nil {
            let digitized = exif[kCGImagePropertyExifDateTimeDigitized as String] as? String
            let value = digitized ?? tiff[kCGImagePropertyTIFFDateTime as String] as? String
            let offsetKey = digitized == nil ? "OffsetTime" : "OffsetTimeDigitized"
            if let value {
                let sourceZone = try (exif[offsetKey] as? String).map(timeZone) ?? result.acquisitionTimeZone
                let date = try parse(value, timeZone: sourceZone)
                let formatter = formatter(timeZone: result.acquisitionTimeZone)
                formatter.dateFormat = "yyyyMMdd"
                result.additionalAttributes.setString(formatter.string(from: date), for: .contentDate, vr: .DA)
                formatter.dateFormat = "HHmmss"
                result.additionalAttributes.setString(formatter.string(from: date), for: .contentTime, vr: .TM)
            }
        }
        return result
    }

    private static func copyEquipment(tiff: [String: Any], exif: [String: Any],
                                      to result: inout PhotographMetadata) throws {
        if result.manufacturer.isEmpty, let make = tiff[kCGImagePropertyTIFFMake as String] as? String {
            result.manufacturer = make.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        let values = [(tiff[kCGImagePropertyTIFFModel as String], Tag.manufacturerModelName),
                      (tiff[kCGImagePropertyTIFFSoftware as String], Tag.softwareVersions),
                      (exif["BodySerialNumber"], Tag.deviceSerialNumber)]
        for (value, tag) in values where result.additionalAttributes[tag] == nil {
            if let value = value as? String {
                try MetadataValidation.text(value, maximum: 64)
                result.additionalAttributes.setString(value, for: tag, vr: .LO)
            }
        }
        for key in ["ApertureValue", "ShutterSpeedValue"] {
            guard let value = exif[key] as? NSNumber else { continue }
            guard let entry = DataElementDictionary.lookup(keyword: key) else {
                throw MaterializationError.invalidTerminology(key)
            }
            if result.additionalAttributes[entry.tag] == nil {
                guard value.doubleValue.isFinite else {
                    throw MaterializationError.invalidMetadata("Non-finite EXIF exposure value")
                }
                result.additionalAttributes.setString(DICOMDecimalString(value: value.doubleValue).dicomString,
                                                       for: entry.tag, vr: .DS)
            }
        }
    }

    private static func formatter(timeZone: TimeZone) -> DateFormatter {
        let result = DateFormatter()
        result.locale = Locale(identifier: "en_US_POSIX")
        result.calendar = Calendar(identifier: .gregorian)
        result.timeZone = timeZone
        result.isLenient = false
        result.dateFormat = "yyyy:MM:dd HH:mm:ss"
        return result
    }

    private static func parse(_ value: String, timeZone: TimeZone) throws -> Date {
        let formatter = formatter(timeZone: timeZone)
        guard let date = formatter.date(from: value), formatter.string(from: date) == value else {
            throw MaterializationError.invalidMetadata("EXIF timestamp is malformed")
        }
        return date
    }

    private static func timeZone(_ value: String) throws -> TimeZone {
        let bytes = Array(value.utf8)
        guard bytes.count == 6, [43, 45].contains(bytes[0]), bytes[3] == 58,
              [bytes[1], bytes[2], bytes[4], bytes[5]].allSatisfy({ (48...57).contains($0) }) else {
            throw MaterializationError.invalidMetadata("EXIF time offset is malformed")
        }
        let hours = Int(bytes[1] - 48) * 10 + Int(bytes[2] - 48)
        let minutes = Int(bytes[4] - 48) * 10 + Int(bytes[5] - 48)
        let seconds = (hours * 3600 + minutes * 60) * (bytes[0] == 45 ? -1 : 1)
        guard (-12 * 3600...14 * 3600).contains(seconds), minutes < 60,
              let result = TimeZone(secondsFromGMT: seconds) else {
            throw MaterializationError.invalidMetadata("EXIF time offset is out of range")
        }
        return result
    }
}
#endif
