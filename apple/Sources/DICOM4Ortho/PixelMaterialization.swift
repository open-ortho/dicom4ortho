// Assembles VL image pixels and delegates actual encoding/writing to DICOMKit.
// Private codec intermediates are not published predecessors with separate identity.
import Foundation
import DICOMCore
import DICOMKit

enum PixelMaterialization {
    static func rgb8(
        _ pixels: Data, width: Int, height: Int, metadata: PhotographMetadata,
        encoding: PhotographEncoding
    ) throws -> DICOMFile {
        if let quality = encoding.quality {
            guard quality.isFinite, quality > 0, quality < 1 else {
                throw MaterializationError.invalidCompressionQuality
            }
        }
        let (area, overflow) = width.multipliedReportingOverflow(by: height)
        let (byteCount, byteOverflow) = area.multipliedReportingOverflow(by: 3)
        guard (1...65535).contains(width), (1...65535).contains(height),
              !overflow, !byteOverflow, pixels.count == byteCount else {
            throw MaterializationError.invalidPixelData
        }
        var dataset = try PhotographProfile().makeMetadata(metadata)
        layout(width: width, height: height, to: &dataset)
        dataset.setString("RGB", for: .photometricInterpretation, vr: .CS)
        let previousLoss = metadata.additionalAttributes.string(for: .lossyImageCompression) == "01"
        dataset.setString(previousLoss ? "01" : "00", for: .lossyImageCompression, vr: .CS)
        if previousLoss {
            for tag in [Tag.lossyImageCompressionMethod, .lossyImageCompressionRatio] {
                dataset[tag] = metadata.additionalAttributes[tag]
            }
        }
        dataset[.pixelData] = .data(tag: .pixelData, vr: .OB, data: pixels)
        return try encode(dataset, metadata: metadata, encoding: encoding)
    }

    static func encode(_ dataset: DataSet, metadata: PhotographMetadata,
                       encoding: PhotographEncoding) throws -> DICOMFile {
        let native = DICOMFile.create(dataSet: dataset)
        if encoding == .explicitLittleEndian || encoding == .preserveSource { return native }
        let bytes = try CompressionManager().compressData(
            native.write(), codec: encoding.codecName, quality: encoding.quality.map { .custom($0) })
        let file = try DICOMFile.read(from: bytes)
        var finalDataset = file.dataSet
        finalDataset.setString(metadata.sopInstanceUID, for: .sopInstanceUID, vr: .UI)
        return DICOMFile.create(dataSet: finalDataset, transferSyntaxUID: file.transferSyntaxUID!)
    }

    static func layout(width: Int, height: Int, to dataset: inout DataSet) {
        dataset.setUInt16(UInt16(height), for: .rows)
        dataset.setUInt16(UInt16(width), for: .columns)
        dataset.setUInt16(3, for: .samplesPerPixel)
        dataset.setUInt16(0, for: .planarConfiguration)
        dataset.setUInt16(8, for: .bitsAllocated)
        dataset.setUInt16(8, for: .bitsStored)
        dataset.setUInt16(7, for: .highBit)
        dataset.setUInt16(0, for: .pixelRepresentation)
    }

    static func encapsulate(_ stream: Data, width: Int, height: Int,
                            photometric: String, lossy: Bool, method: String,
                            metadata: PhotographMetadata, syntax: TransferSyntax) throws -> DICOMFile {
        guard (1...65535).contains(width), (1...65535).contains(height) else {
            throw MaterializationError.invalidPixelData
        }
        var dataset = try PhotographProfile().makeMetadata(metadata)
        layout(width: width, height: height, to: &dataset)
        dataset.setString(photometric, for: .photometricInterpretation, vr: .CS)
        dataset.setString(lossy ? "01" : "00", for: .lossyImageCompression, vr: .CS)
        if lossy {
            dataset.setString(method, for: .lossyImageCompressionMethod, vr: .CS)
            let ratio = Double(width) * Double(height) * 3 / Double(stream.count)
            dataset.setString(DICOMDecimalString(value: ratio).dicomString,
                              for: .lossyImageCompressionRatio, vr: .DS)
        }
        dataset[.pixelData] = DataElement(
            tag: .pixelData, vr: .OB, length: .max, valueData: Data(),
            encapsulatedFragments: [stream], encapsulatedOffsetTable: [0])
        return DICOMFile.create(dataSet: dataset, transferSyntaxUID: syntax.uid)
    }
}
