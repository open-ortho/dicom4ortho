// Loads the reviewed bundled mapping; there is no live terminology access at runtime.
// Fields mirror the interchange resource, not an independently maintained clinical catalog.
import Foundation
import DICOMCore
import DICOMKit

struct Terminology: Decodable, Sendable {
    struct Code: Decodable, Sendable {
        let value: String
        let scheme: String
        let meaning: String

        var dataSet: DataSet {
            var result = DataSet()
            result.setString(value, for: .codeValue, vr: .SH)
            result.setString(scheme, for: .codingSchemeDesignator, vr: .SH)
            result.setString(meaning, for: .codeMeaning, vr: .LO)
            return result
        }
    }

    struct ImageType: Decodable, Sendable {
        let keyword: String
        let abbreviation: String
        let meaning: String
        let code: Code
    }

    struct View: Decodable, Sendable {
        let keyword: String
        let patientOrientation: [String]?
        let imageLaterality: String
        let anatomicRegion: Code
        let anatomicRegionModifier: Code?
        let primaryAnatomicStructure: Code?
        let primaryAnatomicStructureModifier: Code?
        let devices: [Code]
        let viewCode: Code?
        let viewModifiers: [Code]
        let orthognathicFunctionalConditions: [Code]
        let findingsByInspection: [Code]
        let observableEntities: [Code]
        let dentalOcclusion: Code?
        let description: String
        let seriesDescription: String

        private enum CodingKeys: String, CodingKey {
            case keyword, devices, description
            case patientOrientation = "patient_orientation"
            case imageLaterality = "image_laterality"
            case anatomicRegion = "anatomic_region"
            case anatomicRegionModifier = "anatomic_region_modifier"
            case primaryAnatomicStructure = "primary_anatomic_structure"
            case primaryAnatomicStructureModifier = "primary_anatomic_structure_modifier"
            case viewCode = "view_code"
            case viewModifiers = "view_modifiers"
            case orthognathicFunctionalConditions = "orthognathic_functional_conditions"
            case findingsByInspection = "findings_by_inspection"
            case observableEntities = "observable_entities"
            case dentalOcclusion = "dental_occlusion"
            case seriesDescription = "series_description"
        }
    }

    let codes: [String: Code]
    let imageTypes: [String: ImageType]
    let views: [String: View]

    private enum CodingKeys: String, CodingKey {
        case codes, views
        case imageTypes = "image_types"
    }

    static func bundled() throws -> Self {
        guard let url = Bundle.module.url(forResource: "terminology", withExtension: "json") else {
            throw MaterializationError.invalidTerminology("Missing bundled terminology.json")
        }
        return try JSONDecoder().decode(Self.self, from: Data(contentsOf: url))
    }
}
