// Exports synthetic outputs for independent decoding; a successful DICOMKit
// self-read is necessary for serialization checks, not sufficient codec qualification.
import Foundation
import Testing
import DICOMCore
import DICOMKit
@testable import DICOM4Ortho

private let encodings: [(String, PhotographEncoding)] = [
    ("explicit-le", .explicitLittleEndian), ("implicit-le", .implicitLittleEndian),
    ("jpeg-baseline", .jpegBaseline(quality: 0.9)), ("jpeg-lossless", .jpegLossless),
    ("jpeg-ls-lossless", .jpegLSLossless), ("jpeg2000-lossless", .jpeg2000Lossless),
    ("jpeg2000-lossy", .jpeg2000Lossy(quality: 0.9)), ("htj2k-lossless", .htj2kLossless),
    ("htj2k-rpcl", .htj2kLosslessRPCL), ("htj2k-lossy", .htj2kLossy(quality: 0.9)),
    ("jpeg-xl-lossless", .jpegXLLossless), ("jpeg-xl-lossy", .jpegXLLossy(quality: 0.9)),
    ("rle", .rleLossless)
]

@Test func encodeSyntheticRGBPhotographs() throws {
    let size = Int(ProcessInfo.processInfo.environment["DICOM4ORTHO_TEST_IMAGE_SIZE"] ?? "64") ?? 64
    guard (16...4096).contains(size) else { throw MaterializationError.invalidPixelData }
    var samples = Data()
    for y in 0..<size {
        for x in 0..<size {
            samples.append(contentsOf: [UInt8(truncatingIfNeeded: x * 4),
                                       UInt8(truncatingIfNeeded: y * 4),
                                       UInt8(truncatingIfNeeded: (x + y) * 2)])
        }
    }
    for (name, encoding) in encodings {
        let metadata = PhotographMetadata(imageType: "EV01")
        let photo = try OrthodonticPhotograph(
            image: .rgb8(samples, width: size, height: size), metadata: metadata, encoding: encoding)
        let bytes = try photo.dicomData()
        #expect(try photo.dicomData() == bytes)
        let file = try DICOMFile.read(from: bytes)
        #expect(file.transferSyntaxUID == CompressionManager.transferSyntax(for: encoding.codecName)?.uid)
        #expect(file.dataSet.string(for: .lossyImageCompression) == (encoding.quality == nil ? "00" : "01"))
        #expect(file.sopInstanceUID == metadata.sopInstanceUID)
        #expect(file.sopInstanceUID == file.fileMetaInformation.string(for: .mediaStorageSOPInstanceUID))
        if let directory = ProcessInfo.processInfo.environment["DICOM4ORTHO_TEST_ARTIFACTS"] {
            let url = URL(fileURLWithPath: directory, isDirectory: true)
            try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
            try bytes.write(to: url.appendingPathComponent(name + ".dcm"))
            try samples.write(to: url.appendingPathComponent("source.rgb"))
            try JSONSerialization.data(withJSONObject: ["width": size, "height": size])
                .write(to: url.appendingPathComponent("source.json"))
        }
    }
}
