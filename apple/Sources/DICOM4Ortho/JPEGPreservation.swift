// Validates the supported JPEG frame header before encapsulating the original stream.
// This is a preservation adapter, not a JPEG encoder/decoder. DICOMKit exposes frame
// components but not SOF process/dimensions, so only that missing header check is local.
import Foundation
import DICOMCore
import DICOMKit

enum JPEGPreservation {
    static func preserve(_ data: Data, metadata: PhotographMetadata) throws -> DICOMFile {
        let bytes = [UInt8](data)
        guard bytes.count >= 4, bytes.prefix(2) == [0xff, 0xd8],
              bytes.suffix(2) == [0xff, 0xd9] else { throw MaterializationError.unsupportedImage }
        var position = 2
        while position + 4 <= bytes.count {
            guard bytes[position] == 0xff else { throw MaterializationError.unsupportedImage }
            let marker = bytes[position + 1]
            if marker == 0xff { position += 1; continue }
            let length = Int(bytes[position + 2]) * 256 + Int(bytes[position + 3])
            guard length >= 2, length <= bytes.count - position - 2 else {
                throw MaterializationError.unsupportedImage
            }
            let isFrame = (0xc0...0xcf).contains(marker) && ![0xc4, 0xc8, 0xcc].contains(marker)
            if isFrame {
                guard marker == 0xc0, length == 17, bytes[position + 4] == 8,
                      bytes[position + 9] == 3,
                      let components = JPEGInterchangeFormat.frameComponents(in: data),
                      components.map(\.identifier) == [1, 2, 3]
                        || (components.map(\.identifier) == [0, 1, 2]
                            && JPEGInterchangeFormat.containsJFIFSegment(data)) else {
                    throw MaterializationError.unsupportedImage
                }
                let height = Int(bytes[position + 5]) * 256 + Int(bytes[position + 6])
                let width = Int(bytes[position + 7]) * 256 + Int(bytes[position + 8])
                return try PixelMaterialization.encapsulate(
                    data, width: width, height: height, photometric: "YBR_FULL_422", lossy: true,
                    method: "ISO_10918_1", metadata: metadata, syntax: .jpegBaseline)
            }
            guard marker != 0xda, marker != 0xd9 else { throw MaterializationError.unsupportedImage }
            position += length + 2
        }
        throw MaterializationError.unsupportedImage
    }
}
