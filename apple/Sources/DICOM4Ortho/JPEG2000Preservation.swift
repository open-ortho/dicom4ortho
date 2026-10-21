// Preserves supported JPEG 2000 / HTJ2K codestreams using dependency container and
// marker readers. A reversible wavelet alone does not prove an externally supplied
// codestream is lossless: rate truncation and previous lossy processing are separate facts.
import Foundation
import DICOMCore
import DICOMKit
import J2KCore
import J2KFileFormat

enum JPEG2000Preservation {
    static func preserve(_ data: Data, metadata: PhotographMetadata) throws -> DICOMFile {
        let stream: Data
        let format = try J2KFormatDetector().detect(data: data)
        switch format {
        case .j2k:
            // A raw codestream has no independent color-space declaration.
            guard metadata.additionalAttributes.string(for: .photometricInterpretation) == "RGB" else {
                throw MaterializationError.invalidMetadata("Raw JPEG 2000 requires an explicit RGB source declaration")
            }
            stream = data
        case .jp2:
            stream = try jp2Codestream(data)
        default: throw MaterializationError.unsupportedImage
        }
        guard stream.suffix(2) == [0xff, 0xd9],
              let style = J2KCodestreamInspector.codingStyle(in: stream),
              style.componentCount == 3, style.multipleComponentTransform == 1,
              !style.hasCodingStyleOverride,
              !J2KCodestreamInspector.containsPart2MultiComponentTransform(in: stream),
              let siz = try J2KMarkerParser(data: stream).parseMainHeader().first(where: { $0.marker == .siz }) else {
            throw MaterializationError.unsupportedImage
        }
        // The dependency exposes raw SIZ segment data, not its component descriptors.
        // Read only precision/subsampling/origin facts missing from CodingStyle.
        var reader = J2KBitReader(data: siz.data)
        let capabilities = try reader.readUInt16()
        guard capabilities == 0 || HTJ2KCodec.isHTJ2K(stream) else {
            throw MaterializationError.unsupportedImage
        }
        _ = try reader.readUInt32() // grid width
        _ = try reader.readUInt32() // grid height
        guard try reader.readUInt32() == 0, try reader.readUInt32() == 0 else {
            throw MaterializationError.unsupportedImage
        }
        for _ in 0..<4 { _ = try reader.readUInt32() } // tile size and origin
        guard try reader.readUInt16() == 3 else { throw MaterializationError.unsupportedImage }
        for _ in 0..<3 {
            guard try reader.readUInt8() == 7, try reader.readUInt8() == 1,
                  try reader.readUInt8() == 1 else { throw MaterializationError.unsupportedImage }
        }
        let irreversible = J2KCodestreamInspector.usesIrreversibleWavelet(in: stream)
        let history = metadata.additionalAttributes.string(for: .lossyImageCompression)
        if !irreversible && history != "00" && history != "01" {
            throw MaterializationError.invalidMetadata(
                "JPEG 2000 with reversible wavelets requires source LossyImageCompression evidence (00 or 01)")
        }
        if irreversible && history == "00" {
            throw MaterializationError.invalidMetadata("Irreversible JPEG 2000 cannot declare a lossless source")
        }
        let lossy = irreversible || history == "01"
        let ht = HTJ2KCodec.isHTJ2K(stream)
        let syntax: TransferSyntax = ht ? (lossy ? .htj2kLossy : .htj2kLossless)
            : (lossy ? .jpeg2000 : .jpeg2000Lossless)
        let photometric = style.multipleComponentTransform == 0 ? "RGB" : (irreversible ? "YBR_ICT" : "YBR_RCT")
        return try PixelMaterialization.encapsulate(
            stream, width: style.gridWidth, height: style.gridHeight, photometric: photometric,
            lossy: lossy, method: ht ? "ISO_15444_15" : "ISO_15444_1", metadata: metadata, syntax: syntax)
    }

    private static func jp2Codestream(_ data: Data) throws -> Data {
        var reader = J2KBoxReader(data: data)
        let boxes = try checkedBoxes(&reader)
        guard let header = boxes.first(where: { $0.type == .jp2h }),
              boxes.filter({ $0.type == .jp2c }).count == 1,
              let codestream = boxes.first(where: { $0.type == .jp2c }) else {
            throw MaterializationError.unsupportedImage
        }
        var headerReader = J2KBoxReader(data: reader.extractContent(from: header))
        let children = try checkedBoxes(&headerReader)
        guard !children.contains(where: { [.pclr, .cmap, .cdef].contains($0.type) }),
              children.filter({ $0.type == .colr }).count == 1,
              let color = children.first(where: { $0.type == .colr }) else {
            throw MaterializationError.unsupportedImage
        }
        var specification = J2KColorSpecificationBox(method: .enumerated(.sRGB))
        try specification.read(from: headerReader.extractContent(from: color))
        guard specification.method == .enumerated(.sRGB) else {
            throw MaterializationError.unsupportedImage
        }
        return reader.extractContent(from: codestream)
    }

    private static func checkedBoxes(_ reader: inout J2KBoxReader) throws -> [J2KBoxReader.BoxInfo] {
        var boxes: [J2KBoxReader.BoxInfo] = []
        // The dependency's readAllBoxes can fail to advance on an extended zero
        // length. Guard progress before advancing; do not duplicate its box parser.
        while let box = try reader.peekNextBox() {
            guard box.totalLength >= box.headerSize else { throw MaterializationError.unsupportedImage }
            boxes.append(box)
            try reader.skipBox()
        }
        return boxes
    }
}
