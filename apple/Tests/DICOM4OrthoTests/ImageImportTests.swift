// Tests input evidence, file boundaries, and source-history semantics with synthetic
// images only. No application cameras, patient images, or network services are used.
import Foundation
import Testing
import DICOMCore
import DICOMKit
import J2KCore
import J2KFileFormat
import CoreGraphics
import ImageIO
@testable import DICOM4Ortho

private func syntheticRGB() -> Data {
    Data((0..<(64 * 64 * 3)).map { UInt8(truncatingIfNeeded: $0) })
}

private func encodedImage(type: String, exif: Bool = false, offset: String? = nil) throws -> Data {
    let data = NSMutableData()
    guard let provider = CGDataProvider(data: syntheticRGB() as CFData),
          let image = CGImage(width: 64, height: 64, bitsPerComponent: 8, bitsPerPixel: 24,
                              bytesPerRow: 64 * 3, space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGBitmapInfo(rawValue: 0), provider: provider,
                              decode: nil, shouldInterpolate: false, intent: .defaultIntent),
          let destination = CGImageDestinationCreateWithData(data, type as CFString, 1, nil) else {
        throw MaterializationError.unsupportedImage
    }
    var properties: [String: Any] = [:]
    if exif {
        var exifProperties = [
            kCGImagePropertyExifDateTimeOriginal as String: "2026:07:14 12:30:00"]
        if let offset { exifProperties["OffsetTimeOriginal"] = offset }
        properties[kCGImagePropertyExifDictionary as String] = exifProperties
        properties[kCGImagePropertyTIFFDictionary as String] = [kCGImagePropertyTIFFMake as String: "Example Camera"]
    }
    CGImageDestinationAddImage(destination, image, properties as CFDictionary)
    guard CGImageDestinationFinalize(destination) else { throw MaterializationError.unsupportedImage }
    return data as Data
}

@Test func importPNGAndTIFFAndKeepFileAndMemoryBehaviorConsistent() throws {
    for type in ["public.png", "public.tiff", "com.microsoft.bmp"] {
        let bytes = try encodedImage(type: type)
        let metadata = PhotographMetadata(imageType: "EV01")
        let memory = try OrthodonticPhotograph(image: .encoded(bytes), metadata: metadata,
                                               encoding: .explicitLittleEndian)
        #expect(memory.dataSet.uint16(for: .rows) == 64)
        #expect(memory.dataSet.string(for: .lossyImageCompression) == "00")
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let input = directory.appendingPathComponent("wrong-extension.dat")
        try bytes.write(to: input)
        let file = try OrthodonticPhotograph(image: .file(input), metadata: metadata,
                                             encoding: .explicitLittleEndian)
        #expect(file.dataSet[.pixelData]?.valueData == memory.dataSet[.pixelData]?.valueData)
        let output = directory.appendingPathComponent("output.dcm")
        try memory.save(to: output)
        try memory.save(to: output)
        #expect(try Data(contentsOf: output) == memory.dicomData())
    }
}

@Test func preserveJPEGWithoutRecompressionAndRetainLossHistoryWhenTranscoding() throws {
    let stream = try encodedImage(type: "public.jpeg")
    let preserved = try OrthodonticPhotograph(image: .encoded(stream), metadata: .init(imageType: "EV01"))
    #expect(preserved.dataSet[.pixelData]?.encapsulatedFragments?.first == stream)
    #expect(preserved.transferSyntax == .jpegBaseline)
    #expect(preserved.dataSet.strings(for: .imageType)?.first == "ORIGINAL")
    let transcoded = try OrthodonticPhotograph(image: .encoded(stream), metadata: .init(imageType: "EV01"),
                                               encoding: .jpegLSLossless)
    #expect(transcoded.dataSet.string(for: .lossyImageCompression) == "01")
    #expect(transcoded.dataSet.strings(for: .imageType)?.first == "DERIVED")
}

@Test func exifIsFallbackAndExplicitClinicalFactsWin() throws {
    let bytes = try encodedImage(type: "public.jpeg", exif: true)
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.acquisitionTimeZone = TimeZone(secondsFromGMT: 0)!
    let fallback = try OrthodonticPhotograph(image: .encoded(bytes), metadata: metadata,
                                             encoding: .explicitLittleEndian)
    #expect(fallback.dataSet.string(for: .acquisitionDate) == "20260714")
    #expect(fallback.dataSet.string(for: .manufacturer) == "Example Camera")
    metadata.acquisitionDateTime = ISO8601DateFormatter().date(from: "2026-10-21T12:00:00Z")!
    metadata.manufacturer = "Explicit"
    let explicit = try OrthodonticPhotograph(image: .encoded(bytes), metadata: metadata,
                                             encoding: .explicitLittleEndian)
    #expect(explicit.dataSet.string(for: .acquisitionDate) == "20261021")
    #expect(explicit.dataSet.string(for: .manufacturer) == "Explicit")
}

@Test func rawJPEG2000PreservationRequiresColorAndLossEvidence() throws {
    let original = try OrthodonticPhotograph(
        image: .rgb8(syntheticRGB(), width: 64, height: 64), metadata: .init(imageType: "EV01"),
        encoding: .jpeg2000Lossless)
    let stream = original.dataSet[.pixelData]!.encapsulatedFragments![0]
    var metadata = PhotographMetadata(imageType: "EV01")
    #expect(throws: MaterializationError.self) {
        try OrthodonticPhotograph(image: .encoded(stream), metadata: metadata)
    }
    metadata.additionalAttributes.setString("RGB", for: .photometricInterpretation, vr: .CS)
    #expect(throws: MaterializationError.self) {
        try OrthodonticPhotograph(image: .encoded(stream), metadata: metadata)
    }
    metadata.additionalAttributes.setString("00", for: .lossyImageCompression, vr: .CS)
    let preserved = try OrthodonticPhotograph(image: .encoded(stream), metadata: metadata)
    #expect(preserved.dataSet[.pixelData]?.encapsulatedFragments?.first == stream)
    #expect(preserved.transferSyntax == .jpeg2000Lossless)
}

@Test func rejectsMalformedUnsupportedAndRemoteInputs() throws {
    #expect(throws: (any Error).self) {
        try OrthodonticPhotograph(image: .encoded(Data([0, 1, 2])), metadata: .init(imageType: "EV01"))
    }
    #expect(throws: (any Error).self) {
        try OrthodonticPhotograph(image: .file(URL(string: "https://example.invalid/photo.jpg")!),
                                  metadata: .init(imageType: "EV01"))
    }
    let photo = try OrthodonticPhotograph(image: .rgb8(Data([0, 0, 0]), width: 1, height: 1),
                                          metadata: .init(imageType: "EV01"))
    #expect(throws: (any Error).self) { try photo.save(to: URL(string: "https://example.invalid/photo.dcm")!) }
}

@Test func JP2PreservationUsesContainerColorAndKeepsTheOriginalCodestream() throws {
    let original = try OrthodonticPhotograph(
        image: .rgb8(syntheticRGB(), width: 64, height: 64), metadata: .init(imageType: "EV01"),
        encoding: .jpeg2000Lossless)
    let stream = original.dataSet[.pixelData]!.encapsulatedFragments![0]
    let jp2 = try J2KFileWriter(format: .jp2).wrap(
        codestream: stream, headerForImage: J2KImage(width: 64, height: 64, components: 3))
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.additionalAttributes.setString("00", for: .lossyImageCompression, vr: .CS)
    let preserved = try OrthodonticPhotograph(image: .encoded(jp2), metadata: metadata)
    #expect(preserved.dataSet[.pixelData]?.encapsulatedFragments?.first == stream)
    #expect(preserved.dataSet.string(for: .photometricInterpretation) == "YBR_RCT")
}

@Test func rawSamplesAndUncompressedContainersDoNotEraseKnownPreviousLoss() throws {
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.additionalAttributes.setString("01", for: .lossyImageCompression, vr: .CS)
    metadata.additionalAttributes.setString("ISO_10918_1", for: .lossyImageCompressionMethod, vr: .CS)
    metadata.additionalAttributes.setString("8.5", for: .lossyImageCompressionRatio, vr: .DS)
    let raw = try OrthodonticPhotograph(image: .rgb8(syntheticRGB(), width: 64, height: 64), metadata: metadata)
    #expect(raw.dataSet.string(for: .lossyImageCompression) == "01")
    #expect(raw.dataSet.string(for: .lossyImageCompressionRatio) == "8.5")
    let png = try OrthodonticPhotograph(image: .encoded(encodedImage(type: "public.png")),
                                        metadata: metadata, encoding: .explicitLittleEndian)
    #expect(png.dataSet.string(for: .lossyImageCompression) == "01")
    #expect(png.dataSet.string(for: .lossyImageCompressionRatio) == "8.5")
}

@Test func EXIFOffsetControlsAcquisitionRatherThanTheProcessTimezone() throws {
    let bytes = try encodedImage(type: "public.jpeg", exif: true, offset: "+05:30")
    var metadata = PhotographMetadata(imageType: "EV01")
    metadata.acquisitionTimeZone = TimeZone(secondsFromGMT: 0)!
    let photo = try OrthodonticPhotograph(image: .encoded(bytes), metadata: metadata,
                                          encoding: .explicitLittleEndian)
    #expect(photo.dataSet.string(for: .timezoneOffsetFromUTC) == "+0530")
    #expect(photo.dataSet.string(for: .acquisitionTime)?.hasPrefix("123000") == true)
}
