// Converts supported local still-image containers to VL input evidence. ImageIO
// owns decoding/color conversion; DICOMKit's public ImageConverter produces a
// different IOD (Secondary Capture) and requires a URL, so its orchestration is not reused.
import Foundation
import DICOMCore
import DICOMKit
import J2KFileFormat
#if canImport(ImageIO) && canImport(CoreGraphics)
import ImageIO
import CoreGraphics
#endif

enum ImageImport {
    static func materialize(_ bytes: Data, metadata: PhotographMetadata,
                            encoding: PhotographEncoding) throws -> DICOMFile {
        #if canImport(ImageIO) && canImport(CoreGraphics)
        let source = CGImageSourceCreateWithData(bytes as CFData, nil)
        if let source, CGImageSourceGetCount(source) != 1 { throw MaterializationError.unsupportedImage }
        let properties = source.flatMap {
            CGImageSourceCopyPropertiesAtIndex($0, 0, nil) as? [String: Any]
        } ?? [:]
        if let orientation = properties[kCGImagePropertyOrientation as String] as? Int, orientation != 1 {
            // Raw clinical orientation mappings cannot silently ignore an EXIF rotation.
            // Preservation cannot normalize it without changing the source codestream.
            throw MaterializationError.unsupportedImage
        }
        let metadata = try exifFallback(properties, metadata: metadata)
        if encoding == .preserveSource {
            if bytes.starts(with: [0xff, 0xd8]) {
                return try JPEGPreservation.preserve(bytes, metadata: metadata)
            }
            return try JPEG2000Preservation.preserve(bytes, metadata: metadata)
        }
        guard let source, let sourceType = CGImageSourceGetType(source) else {
            throw MaterializationError.unsupportedImage
        }
        let type = sourceType as String
        guard ["public.jpeg", "public.png", "public.tiff", "com.microsoft.bmp", "public.jpeg-2000"].contains(type) else {
            // ImageIO also reads HEIF/GIF and other containers. Accepting all of
            // them would silently assert a compression history we have not qualified.
            throw MaterializationError.unsupportedImage
        }
        if type == "public.tiff" {
            let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
            let compression = tiff?[kCGImagePropertyTIFFCompression as String] as? Int
            // TIFF 6.0 lossless encodings plus the two registered Deflate values.
            // JPEG-in-TIFF and unknown schemes need separate source-history qualification.
            guard let compression, [1, 5, 8, 32773, 32946].contains(compression) else {
                throw MaterializationError.unsupportedImage
            }
        }
        if type == "public.jpeg" {
            let header = try JPEGPreservation.inspect(bytes)
            guard [0xc0, 0xc2].contains(header.process), header.precision == 8 else {
                throw MaterializationError.unsupportedImage
            }
        }
        guard let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
              image.bitsPerComponent == 8,
              [.none, .noneSkipFirst, .noneSkipLast].contains(image.alphaInfo),
              let space = CGColorSpace(name: CGColorSpace.sRGB) else {
            throw MaterializationError.unsupportedImage
        }
        let width = image.width, height = image.height
        guard (1...65535).contains(width), (1...65535).contains(height) else {
            throw MaterializationError.invalidPixelData
        }
        var rgba = Data(count: width * height * 4)
        try rgba.withUnsafeMutableBytes { buffer in
            guard let context = CGContext(
                data: buffer.baseAddress, width: width, height: height, bitsPerComponent: 8,
                bytesPerRow: width * 4, space: space,
                bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue) else {
                throw MaterializationError.unsupportedImage
            }
            context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        }
        var pixels = Data(capacity: width * height * 3)
        for index in stride(from: 0, to: rgba.count, by: 4) {
            pixels.append(contentsOf: rgba[index..<(index + 3)])
        }
        var encodingMetadata = metadata
        // History is appended once below after the new encoder reports its own stage.
        for tag in [Tag.lossyImageCompression, .lossyImageCompressionMethod, .lossyImageCompressionRatio] {
            encodingMetadata.additionalAttributes[tag] = nil
        }
        var file = try PixelMaterialization.rgb8(pixels, width: width, height: height,
                                                metadata: encodingMetadata, encoding: encoding)
        let sourceWasJPEG = bytes.starts(with: [0xff, 0xd8])
        // ImageIO does not expose JPEG 2000 quantization/history. A decoded JP2/J2K
        // needs explicit loss-history evidence rather than silently becoming "00".
        let sourceWasJ2K = (try? J2KFormatDetector().detect(data: bytes)) != nil
        if sourceWasJ2K && !["00", "01"].contains(metadata.additionalAttributes.string(for: .lossyImageCompression) ?? "") {
            throw MaterializationError.invalidMetadata("JPEG 2000 transcoding requires explicit source loss history")
        }
        if sourceWasJ2K && metadata.additionalAttributes.string(for: .lossyImageCompression) == "00"
            && J2KCodestreamInspector.usesIrreversibleWavelet(in: bytes) {
            throw MaterializationError.invalidMetadata("Irreversible JPEG 2000 cannot declare a lossless source")
        }
        if sourceWasJPEG || metadata.additionalAttributes.string(for: .lossyImageCompression) == "01" {
            // Decoding/re-encoding a lossy source does not make its history lossless.
            var dataset = file.dataSet
            dataset.setString("01", for: .lossyImageCompression, vr: .CS)
            dataset.setStrings(["DERIVED", "PRIMARY"], for: .imageType, vr: .CS)
            let sourceMethods: [String]
            let sourceRatios: [String]
            if sourceWasJPEG || sourceWasJ2K {
                sourceMethods = [sourceWasJPEG ? "ISO_10918_1" : "ISO_15444_1"]
                sourceRatios = [DICOMDecimalString(value: Double(width * height * 3) / Double(bytes.count)).dicomString]
            } else {
                // For a PNG exported from a previously lossy image, the PNG byte
                // count does not measure the earlier lossy compression ratio.
                sourceMethods = metadata.additionalAttributes.strings(for: .lossyImageCompressionMethod) ?? []
                sourceRatios = metadata.additionalAttributes.strings(for: .lossyImageCompressionRatio) ?? []
            }
            let methods = sourceMethods + (dataset.strings(for: .lossyImageCompressionMethod) ?? [])
            let ratios = sourceRatios + (dataset.strings(for: .lossyImageCompressionRatio) ?? [])
            if !methods.isEmpty { dataset.setStrings(methods, for: .lossyImageCompressionMethod, vr: .CS) }
            if !ratios.isEmpty { dataset.setStrings(ratios, for: .lossyImageCompressionRatio, vr: .DS) }
            file = DICOMFile.create(dataSet: dataset, transferSyntaxUID: file.transferSyntaxUID!)
        }
        return file
        #else
        throw MaterializationError.unsupportedImage
        #endif
    }

    #if canImport(ImageIO) && canImport(CoreGraphics)
    private static func exifFallback(_ properties: [String: Any], metadata: PhotographMetadata) throws -> PhotographMetadata {
        var result = metadata
        if metadata.manufacturer.isEmpty,
           let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any],
           let make = tiff[kCGImagePropertyTIFFMake as String] as? String {
            result.manufacturer = make.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        guard metadata.acquisitionDateTime == nil,
              let exif = properties[kCGImagePropertyExifDictionary as String] as? [String: Any],
              let date = exif[kCGImagePropertyExifDateTimeOriginal as String] as? String else { return result }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.timeZone = metadata.acquisitionTimeZone
        formatter.isLenient = false
        if let offset = exif["OffsetTimeOriginal"] as? String {
            let bytes = Array(offset.utf8)
            guard bytes.count == 6, [43, 45].contains(bytes[0]), bytes[3] == 58,
                  [bytes[1], bytes[2], bytes[4], bytes[5]].allSatisfy({ (48...57).contains($0) }) else {
                throw MaterializationError.invalidMetadata("EXIF original-time offset is malformed")
            }
            let hours = Int(bytes[1] - 48) * 10 + Int(bytes[2] - 48)
            let minutes = Int(bytes[4] - 48) * 10 + Int(bytes[5] - 48)
            let seconds = (hours * 3600 + minutes * 60) * (bytes[0] == 45 ? -1 : 1)
            guard (-12 * 3600...14 * 3600).contains(seconds), minutes < 60,
                  let zone = TimeZone(secondsFromGMT: seconds) else {
                throw MaterializationError.invalidMetadata("EXIF original-time offset is out of range")
            }
            formatter.timeZone = zone
            result.acquisitionTimeZone = zone
        }
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
        guard let acquired = formatter.date(from: date), formatter.string(from: acquired) == date else {
            throw MaterializationError.invalidMetadata("EXIF DateTimeOriginal is malformed")
        }
        result.acquisitionDateTime = acquired
        return result
    }
    #endif
}
