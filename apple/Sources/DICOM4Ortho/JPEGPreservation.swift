// Validates the supported JPEG frame header before encapsulating the original stream.
// This is a preservation adapter, not a JPEG encoder/decoder. DICOMKit exposes frame
// components but not SOF process/dimensions, so only that missing header check is local.
import Foundation
import DICOMCore
import DICOMKit

enum JPEGPreservation {
    struct Header {
        let process: UInt8
        let precision: UInt8
        let width: Int
        let height: Int
        let yCbCrDeclared: Bool
    }

    static func preserve(_ data: Data, metadata: PhotographMetadata) throws -> DICOMFile {
        let header = try inspect(data)
        guard header.process == 0xc0, header.precision == 8,
              let components = JPEGInterchangeFormat.frameComponents(in: data),
              (components.map(\.identifier) == [1, 2, 3]
                || components.map(\.identifier) == [0, 1, 2]),
              header.yCbCrDeclared else { throw MaterializationError.unsupportedImage }
        return try PixelMaterialization.encapsulate(
            data, width: header.width, height: header.height, photometric: "YBR_FULL_422", lossy: true,
            method: "ISO_10918_1", metadata: metadata, syntax: .jpegBaseline)
    }

    static func inspect(_ data: Data) throws -> Header {
        let bytes = [UInt8](data)
        guard bytes.count >= 4, bytes.prefix(2) == [0xff, 0xd8],
              bytes.suffix(2) == [0xff, 0xd9] else { throw MaterializationError.unsupportedImage }
        var position = 2
        var yCbCr = JPEGInterchangeFormat.containsJFIFSegment(data)
        while position + 4 <= bytes.count {
            guard bytes[position] == 0xff else { throw MaterializationError.unsupportedImage }
            let marker = bytes[position + 1]
            if marker == 0xff { position += 1; continue }
            let length = Int(bytes[position + 2]) * 256 + Int(bytes[position + 3])
            guard length >= 2, length <= bytes.count - position - 2 else {
                throw MaterializationError.unsupportedImage
            }
            if marker == 0xee, length >= 14,
               bytes[(position + 4)..<(position + 9)].elementsEqual(Array("Adobe".utf8)) {
                guard bytes[position + 15] == 1 else { throw MaterializationError.unsupportedImage }
                yCbCr = true
            }
            let isFrame = (0xc0...0xcf).contains(marker) && ![0xc4, 0xc8, 0xcc].contains(marker)
            if isFrame {
                guard length == 17, bytes[position + 9] == 3 else {
                    throw MaterializationError.unsupportedImage
                }
                let height = Int(bytes[position + 5]) * 256 + Int(bytes[position + 6])
                let width = Int(bytes[position + 7]) * 256 + Int(bytes[position + 8])
                return Header(process: marker, precision: bytes[position + 4],
                              width: width, height: height, yCbCrDeclared: yCbCr)
            }
            guard marker != 0xda, marker != 0xd9 else { throw MaterializationError.unsupportedImage }
            position += length + 2
        }
        throw MaterializationError.unsupportedImage
    }
}
