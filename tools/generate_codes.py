#!/usr/bin/env python3
"""Generate the committed terminology lock used by dicom4ortho.

DICOM concepts are resolved from the official NEMA FHIR ValueSets. ADA 1100
image types are resolved from terminology.open-ortho.org. The generated Python
module is committed so package builds and runtime use remain offline.

Usage:
    python tools/generate_codes.py
    make update_resources
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import tarfile
import textwrap
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Ensure the package is importable when running from the repository root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from dicom4ortho.config import URL_DENT_OIP_VIEWS


OUTPUT = Path(__file__).parent.parent / "dicom4ortho" / "_generated_codes.py"
DICOM_FHIR_PACKAGE_VERSION = "2025.3.20250714"
DICOM_FHIR_PACKAGE_URL = (
    f"https://fhir.org/packages/fhir.dicom/{DICOM_FHIR_PACKAGE_VERSION}/package.tgz"
)
SCT_SYSTEM = "http://snomed.info/sct"
DCM_SYSTEM = "http://dicom.nema.org/resources/ontology/DCM"


@dataclass(frozen=True)
class SourceSpec:
    """A named remote FHIR terminology resource."""

    url: str | None = None
    package_member: str | None = None


@dataclass(frozen=True)
class CodeBinding:
    """Select one code from a named FHIR resource and coding system."""

    source: str
    system: str
    code: str


def _dicom_value_set(filename: str) -> SourceSpec:
    return SourceSpec(package_member=f"package/{filename}")


SOURCES = {
    "DCM_CODE_SYSTEM": SourceSpec(package_member="package/CodeSystem-DCM.json"),
    "CID247": _dicom_value_set(
        "ValueSet-dicom-cid-247-LateralityLeftRightOnly.json"
    ),
    "CID4028": _dicom_value_set(
        "ValueSet-dicom-cid-4028-CraniofacialAnatomicRegion.json"
    ),
    "CID4061": _dicom_value_set(
        "ValueSet-dicom-cid-4061-HeadAndNeckPrimaryAnatomicStructure.json"
    ),
    "CID4062": _dicom_value_set("ValueSet-dicom-cid-4062-VLView.json"),
    "CID4063": _dicom_value_set("ValueSet-dicom-cid-4063-VLDentalView.json"),
    "CID4064": _dicom_value_set("ValueSet-dicom-cid-4064-VLViewModifier.json"),
    "CID4065": _dicom_value_set(
        "ValueSet-dicom-cid-4065-VLDentalViewModifier.json"
    ),
    "CID4066": _dicom_value_set(
        "ValueSet-dicom-cid-4066-OrthognathicFunctionalCondition.json"
    ),
    "CID4067": _dicom_value_set(
        "ValueSet-dicom-cid-4067-OrthodonticFindingByInspection.json"
    ),
    "CID4068": _dicom_value_set(
        "ValueSet-dicom-cid-4068-OrthodonticObservableEntity.json"
    ),
    "CID4069": _dicom_value_set("ValueSet-dicom-cid-4069-DentalOcclusion.json"),
    "CID4070": _dicom_value_set(
        "ValueSet-dicom-cid-4070-OrthodonticTreatmentProgress.json"
    ),
    "CID4072": _dicom_value_set(
        "ValueSet-dicom-cid-4072-DevicesForThePurposeOfDentalPhotography.json"
    ),
    "ADA_INTRAORAL_2D": SourceSpec(url=(
        "https://terminology.open-ortho.org/fhir/sid/ada1100/CodeSystem/"
        "intraoral-2d-photographic-scheduled-protocol"
    )),
    "ADA_EXTRAORAL_2D": SourceSpec(url=(
        "https://terminology.open-ortho.org/fhir/sid/ada1100/CodeSystem/"
        "extraoral-2d-photographic-scheduled-protocol"
    )),
}


SYSTEM_TO_SCHEME = {
    SCT_SYSTEM: "SCT",
    DCM_SYSTEM: "DCM",
    "http://unitsofmeasure.org": "UCUM",
}


# Fixed SNOMED concept names, DICOM enumerated values, and UCUM units are
# structural parts of TID 3465 or the image module, not context-group values.
LOCAL_CODES = {
    "FindingByInspection": {
        "code": "118243007", "scheme": "SCT", "meaning": "Finding by inspection",
    },
    "ObservableEntity": {
        "code": "363787002", "scheme": "SCT", "meaning": "Observable entity",
    },
    "DentalOcclusion": {
        "code": "25272006", "scheme": "SCT", "meaning": "Dental occlusion",
    },
    "day": {"code": "d", "scheme": "UCUM", "meaning": "days"},
    "LateralityBoth": {"code": "B", "scheme": "CS", "meaning": "Both"},
    "LateralityLeft": {"code": "L", "scheme": "CS", "meaning": "Left"},
    "LateralityRight": {"code": "R", "scheme": "CS", "meaning": "Right"},
    "LateralityUnpaired": {"code": "U", "scheme": "CS", "meaning": "Unpaired"},
    "OrientationLeft": {
        "code": "P^F", "scheme": "CS", "meaning": "Posterior, Foot",
    },
    "OrientationRight": {
        "code": "A^F", "scheme": "CS", "meaning": "Anterior, Foot",
    },
    "OrientationSupineHeadToFeet": {
        "code": "R^P", "scheme": "CS", "meaning": "Right, Posterior",
    },
    "OrientationProneFeetToHead": {
        "code": "R^A", "scheme": "CS", "meaning": "Right, Anterior",
    },
    "OrientationFront": {
        "code": "L^F", "scheme": "CS", "meaning": "Left, Foot",
    },
    "OrientationBack": {
        "code": "R^F", "scheme": "CS", "meaning": "Right, Foot",
    },
    "OrientationSupineFeetToHead": {
        "code": "L^P", "scheme": "CS", "meaning": "Left, Posterior",
    },
    "OrientationProneHeadToFeet": {
        "code": "L^A", "scheme": "CS", "meaning": "Left, Anterior",
    },
}


CODE_BINDINGS = {
    # TID 3465 DCM concept names
    "OrthognathicFunctionalConditions": CodeBinding(
        "DCM_CODE_SYSTEM", DCM_SYSTEM, "130325"
    ),
    "TemporalEventType": CodeBinding("DCM_CODE_SYSTEM", DCM_SYSTEM, "128741"),
    "OffsetFromEvent": CodeBinding("DCM_CODE_SYSTEM", DCM_SYSTEM, "128740"),

    # CID 247 / 4028 / 4061 anatomy
    "right": CodeBinding("CID247", SCT_SYSTEM, "24028007"),
    "left": CodeBinding("CID247", SCT_SYSTEM, "7771000"),
    "Mouth": CodeBinding("CID4028", SCT_SYSTEM, "123851003"),
    "HeadNeck": CodeBinding("CID4028", SCT_SYSTEM, "774007"),
    "dental_arch_mandibular": CodeBinding("CID4061", SCT_SYSTEM, "88176008"),
    "dental_arch_maxillary": CodeBinding("CID4061", SCT_SYSTEM, "39481002"),
    "StructureOfBuccalSpace": CodeBinding("CID4061", SCT_SYSTEM, "261063000"),
    "frenum": CodeBinding("CID4061", SCT_SYSTEM, "7652006"),
    "FaceStructure": CodeBinding("CID4061", SCT_SYSTEM, "89545001"),
    "OralCavityStructure": CodeBinding("CID4061", SCT_SYSTEM, "74262004"),

    # CID 4062 / 4063 view codes
    "projection_frontal": CodeBinding("CID4062", SCT_SYSTEM, "399033003"),
    "projection_left": CodeBinding("CID4062", SCT_SYSTEM, "399173006"),
    "projection_left_oblique": CodeBinding("CID4062", SCT_SYSTEM, "260421001"),
    "projection_right": CodeBinding("CID4062", SCT_SYSTEM, "399198007"),
    "projection_right_oblique": CodeBinding("CID4062", SCT_SYSTEM, "260424009"),
    "projection_oblique": CodeBinding("CID4062", SCT_SYSTEM, "399182000"),
    "projection_45deg": CodeBinding("CID4062", SCT_SYSTEM, "260454004"),
    "projection_submentovertical": CodeBinding("CID4062", SCT_SYSTEM, "399255003"),
    "projection_vertex": CodeBinding("CID4062", SCT_SYSTEM, "260461000"),
    "projection_occlusal": CodeBinding("CID4063", SCT_SYSTEM, "260499007"),

    # CID 4064 / 4065 view modifiers
    "image_mirrored_uncorrected": CodeBinding("CID4064", SCT_SYSTEM, "789135000"),
    "image_mirrored_uncorrected_flipped_horizontally": CodeBinding(
        "CID4064", SCT_SYSTEM, "789134001"
    ),
    "image_mirrored_uncorrected_flipped_horizontally_vertically": CodeBinding(
        "CID4064", SCT_SYSTEM, "789132002"
    ),
    "image_mirrored_uncorrected_flipped_vertically": CodeBinding(
        "CID4064", SCT_SYSTEM, "789133007"
    ),
    "closeup": CodeBinding("CID4065", SCT_SYSTEM, "789131009"),
    "image_mirrored_corrected": CodeBinding("CID4065", SCT_SYSTEM, "787610003"),
    "image_mirrored_corrected_flipped_horizontally": CodeBinding(
        "CID4065", SCT_SYSTEM, "789310004"
    ),
    "image_mirrored_corrected_flipped_vertically": CodeBinding(
        "CID4065", SCT_SYSTEM, "789311000"
    ),
    "image_mirrored_corrected_flipped_horizontally_vertically": CodeBinding(
        "CID4065", SCT_SYSTEM, "789312007"
    ),
    "image_extraoral_45deg": CodeBinding("CID4065", SCT_SYSTEM, "787612006"),
    "image_extraoral_mpf": CodeBinding("CID4065", SCT_SYSTEM, "787611004"),
    "image_anterior_teeth": CodeBinding("CID4065", SCT_SYSTEM, "789313002"),
    "image_face_lips_relaxed": CodeBinding("CID4065", SCT_SYSTEM, "789314008"),
    "image_lips_closed": CodeBinding("CID4065", SCT_SYSTEM, "787607005"),
    "image_mouth_partially_open_teeth_apart": CodeBinding(
        "CID4065", SCT_SYSTEM, "789130005"
    ),

    # TID 3465 value context groups
    "mouth_open": CodeBinding("CID4066", SCT_SYSTEM, "262016004"),
    "mouth_partially_open": CodeBinding("CID4066", SCT_SYSTEM, "1332210001"),
    "lips_relaxed": CodeBinding("CID4066", SCT_SYSTEM, "1336028006"),
    "lips_closed": CodeBinding("CID4066", SCT_SYSTEM, "1336029003"),
    "mpf": CodeBinding("CID4066", SCT_SYSTEM, "1336026005"),
    "smile": CodeBinding("CID4066", SCT_SYSTEM, "225583004"),
    "skin_mark": CodeBinding("CID4067", SCT_SYSTEM, "276470008"),
    "tattoo": CodeBinding("CID4067", SCT_SYSTEM, "341000119102"),
    "gingival_recession": CodeBinding("CID4067", SCT_SYSTEM, "4356008"),
    "cant": CodeBinding("CID4067", SCT_SYSTEM, "710793000"),
    "pigmentation_mucosa_left": CodeBinding("CID4067", SCT_SYSTEM, "1264188003"),
    "pigmentation_mucosa_right": CodeBinding("CID4067", SCT_SYSTEM, "1264193000"),
    "pigmentation_mucosa_soft_palate": CodeBinding(
        "CID4067", SCT_SYSTEM, "1260043007"
    ),
    "pigmentation_mucosa_lip_lower": CodeBinding(
        "CID4067", SCT_SYSTEM, "1260047008"
    ),
    "pigmentation_mucosa_lip_upper": CodeBinding(
        "CID4067", SCT_SYSTEM, "1260049006"
    ),
    "palsy": CodeBinding("CID4068", SCT_SYSTEM, "193093009"),
    "tongue_thrust": CodeBinding("CID4068", SCT_SYSTEM, "110343009"),
    "co": CodeBinding("CID4069", SCT_SYSTEM, "110320000"),
    "cr": CodeBinding("CID4069", SCT_SYSTEM, "736783005"),
    "PatientRegistration": CodeBinding("CID4070", SCT_SYSTEM, "184047000"),
    "OrthodonticTreatmentStarted": CodeBinding(
        "CID4070", SCT_SYSTEM, "1332161000"
    ),
    "OrthodonticTreatmentStopped": CodeBinding(
        "CID4070", SCT_SYSTEM, "1340210007"
    ),

    # CID 4072 devices
    "device_periodontal_probe": CodeBinding("CID4072", SCT_SYSTEM, "462735007"),
    "device_mirror": CodeBinding("CID4072", SCT_SYSTEM, "1332162007"),
    "device_tongue_depressor": CodeBinding("CID4072", SCT_SYSTEM, "39802000"),
    "device_ruler": CodeBinding("CID4072", SCT_SYSTEM, "102304005"),
    "device_retractor": CodeBinding("CID4072", SCT_SYSTEM, "53535004"),
    "device_contraster": CodeBinding("CID4072", SCT_SYSTEM, "1332163002"),
    "device_fiducial_marker": CodeBinding("CID4072", SCT_SYSTEM, "1332164008"),
}


def _fetch_json(url: str) -> dict:
    """Fetch one FHIR JSON resource."""
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def _fetch_package_json(url: str, members: set[str]) -> dict[str, dict]:
    """Fetch selected JSON resources from a FHIR NPM package."""
    with urllib.request.urlopen(url) as response:
        package_bytes = response.read()
    resources = {}
    with tarfile.open(fileobj=io.BytesIO(package_bytes), mode="r:gz") as package:
        for member in members:
            extracted = package.extractfile(member)
            if extracted is None:
                raise ValueError(f"FHIR package does not contain {member}")
            resources[member] = json.load(extracted)
    return resources


def _fetch_csv(url: str) -> list[dict]:
    """Fetch a CSV resource and return its rows."""
    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def _resource_concepts(resource: dict) -> list[tuple[str, str, str]]:
    """Return (system URI, code, display) concepts from a FHIR resource."""
    resource_type = resource.get("resourceType")
    concepts = []
    if resource_type == "ValueSet":
        for include in resource.get("compose", {}).get("include", []):
            if include.get("filter"):
                raise ValueError("Filter-based FHIR ValueSet includes are not supported")
            system = include.get("system", "")
            for concept in include.get("concept", []):
                concepts.append((system, concept["code"], concept.get("display", "")))
    elif resource_type == "CodeSystem":
        system = resource.get("url", "")
        for concept in resource.get("concept", []):
            concepts.append((system, concept["code"], concept.get("display", "")))
    else:
        raise ValueError(f"Unsupported FHIR resource type: {resource_type!r}")
    return concepts


def resolve_code(resource: dict, binding: CodeBinding) -> dict[str, str]:
    """Resolve exactly one bound code from a FHIR resource."""
    matches = [
        display
        for system, code, display in _resource_concepts(resource)
        if system == binding.system and code == binding.code
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one {binding.system}|{binding.code} in {binding.source}; "
            f"found {len(matches)}"
        )
    try:
        scheme = SYSTEM_TO_SCHEME[binding.system]
    except KeyError as error:
        raise ValueError(f"No DICOM scheme mapping for {binding.system}") from error
    return {"code": binding.code, "scheme": scheme, "meaning": matches[0]}


def _ada_scheme(resource: dict) -> str:
    for identifier in resource.get("identifier", []):
        if identifier.get("system") == "http://dicom.nema.org/resources/ontology/DCM":
            return identifier["value"]
    raise ValueError(f"No DICOM coding scheme identifier in {resource.get('url')}")


def _ada_abbreviation(concept: dict) -> str:
    for designation in concept.get("designation", []):
        value = designation.get("value", "")
        if "." in value and not value.startswith(("EV-", "IV-")):
            return value
    raise ValueError(f"No ADA abbreviation for {concept.get('code')}")


def load_terminology(
    fetch_json: Callable[[str], dict] = _fetch_json,
    fetch_package: Callable[[str, set[str]], dict[str, dict]] = _fetch_package_json,
) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """Load authoritative codes, ADA image types, and source versions."""
    package_members = {
        spec.package_member for spec in SOURCES.values() if spec.package_member
    }
    package_resources = fetch_package(DICOM_FHIR_PACKAGE_URL, package_members)
    resources = {}
    for name, spec in SOURCES.items():
        if spec.package_member:
            resources[name] = package_resources[spec.package_member]
        elif spec.url:
            resources[name] = fetch_json(spec.url)
        else:
            raise ValueError(f"Terminology source {name} has no location")
    codes = dict(LOCAL_CODES)
    for keyword, binding in CODE_BINDINGS.items():
        codes[keyword] = resolve_code(resources[binding.source], binding)

    image_types = {}
    for source in ("ADA_INTRAORAL_2D", "ADA_EXTRAORAL_2D"):
        resource = resources[source]
        scheme = _ada_scheme(resource)
        for concept in resource.get("concept", []):
            keyword = concept["code"]
            if keyword in image_types:
                raise ValueError(f"Duplicate ADA image type: {keyword}")
            image_types[keyword] = {
                "keyword": keyword,
                "abbreviation": _ada_abbreviation(concept),
                "display": concept["display"],
                "meaning": concept.get("definition", concept["display"]),
                "scheme": scheme,
            }

    versions = {
        name: resource.get("version", "unversioned")
        for name, resource in resources.items()
    }
    versions["DICOM_FHIR_PACKAGE"] = DICOM_FHIR_PACKAGE_VERSION
    return codes, image_types, versions


def load_views() -> list[dict]:
    """Return local view-layout rows, excluding the metadata row."""
    rows = _fetch_csv(URL_DENT_OIP_VIEWS)
    return [row for row in rows if not row["keyword"].startswith("VER:")]


def _to_const(keyword: str) -> str:
    """Convert a keyword to a Python UPPER_SNAKE_CASE constant name."""
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", keyword)
    value = re.sub(r"[^a-zA-Z0-9]", "_", value)
    return value.upper().strip("_")


def _code_repr(keyword: str, codes: dict[str, dict]) -> str:
    if not keyword:
        return "None"
    if keyword not in codes:
        raise KeyError(f"Unknown code keyword: {keyword!r}")
    return _to_const(keyword)


def _multi_code_repr(cell: str, codes: dict[str, dict]) -> str:
    if not cell:
        return "()"
    parts = [keyword.strip() for keyword in cell.split("^") if keyword.strip()]
    return "(" + ", ".join(_code_repr(keyword, codes) for keyword in parts) + ",)"


def _render_dicom_code_const(keyword: str, info: dict) -> str:
    meaning = info["meaning"].replace('"', '\\"')[:64]
    return (
        f"{_to_const(keyword)} = DicomCode(\n"
        f"    value={info['code']!r},\n"
        f"    scheme={info['scheme']!r},\n"
        f"    meaning={meaning!r},\n"
        f")"
    )


def _render_ortho_view(
    row: dict, codes: dict[str, dict], image_types: dict[str, dict]
) -> str:
    keyword = row["keyword"]
    image_type = image_types[keyword]
    orientation_keyword = row.get("PatientOrientation", "").strip()
    if orientation_keyword:
        orientation = codes[orientation_keyword]["code"].split("^")
        patient_orientation = f"({orientation[0]!r}, {orientation[1]!r})"
    else:
        patient_orientation = "None"

    laterality_keyword = row.get("ImageLaterality", "").strip()
    image_laterality = (
        repr(codes[laterality_keyword]["code"]) if laterality_keyword else repr("")
    )

    def optional(column: str) -> str:
        return _code_repr(row.get(column, "").strip(), codes)

    def multiple(column: str) -> str:
        return _multi_code_repr(row.get(column, "").strip(), codes)

    series = row.get("SeriesDescription", "").strip().replace('"', '\\"')
    return textwrap.dedent(f"""\
        OrthoView(
            keyword={keyword!r},
            patient_orientation={patient_orientation},
            image_laterality={image_laterality},
            anatomic_region={optional('AnatomicRegionSequence')},
            anatomic_region_modifier={optional('AnatomicRegionModifierSequence')},
            primary_anatomic_structure={optional('PrimaryAnatomicStructureSequence')},
            primary_anatomic_structure_modifier={optional('PrimaryAnatomicStructureModifierSequence')},
            devices={multiple('DeviceSequence')},
            view_code={optional('ViewCodeSequence')},
            view_modifiers={multiple('ViewModifierCodeSequence')},
            orthognathic_functional_conditions={multiple('AcquisitionContextSequence^OrthognathicFunctionalConditions')},
            findings_by_inspection={multiple('AcquisitionContextSequence^FindingByInspection')},
            observable_entities={multiple('AcquisitionContextSequence^ObservableEntity')},
            dental_occlusion={optional('AcquisitionContextSequence^DentalOcclusion')},
            description={image_type['meaning']!r},
            series_description={series!r},
        )""")


def generate(
    codes: dict[str, dict],
    image_types: dict[str, dict],
    views: list[dict],
    source_versions: dict[str, str],
) -> str:
    """Render the generated Python terminology lock."""
    lines = [
        '"""',
        "Auto-generated by tools/generate_codes.py - DO NOT EDIT MANUALLY.",
        "Regenerate with: python tools/generate_codes.py",
        '"""',
        "",
        "from __future__ import annotations",
        "from dicom4ortho.m_dent_oip import AdaImageType, DicomCode, OrthoView",
        "",
        "",
        "SOURCE_VERSIONS: dict[str, str] = {",
    ]
    for name, version in source_versions.items():
        lines.append(f"    {name!r}: {version!r},")
    lines.extend(["}", "", ""])

    emitted_constants = set()
    for keyword, info in codes.items():
        constant = _to_const(keyword)
        if constant in emitted_constants:
            raise ValueError(f"Code keywords produce duplicate constant {constant}")
        emitted_constants.add(constant)
        lines.extend([_render_dicom_code_const(keyword, info), ""])

    lines.extend(["", "CODES: dict[str, DicomCode] = {"])
    for keyword in codes:
        lines.append(f"    {keyword!r}: {_to_const(keyword)},")
    lines.extend(["}", "", "", "IMAGE_TYPES: dict[str, AdaImageType] = {"])
    for keyword, image_type in image_types.items():
        lines.extend([
            f"    {keyword!r}: AdaImageType(",
            f"        keyword={keyword!r},",
            f"        abbreviation={image_type['abbreviation']!r},",
            f"        meaning={image_type['meaning']!r},",
            f"        code=DicomCode(value={keyword!r}, scheme={image_type['scheme']!r}, "
            f"meaning={image_type['display'][:64]!r}),",
            "    ),",
        ])
    lines.extend(["}", "", "", "VIEWS: dict[str, OrthoView] = {"])
    for row in views:
        keyword = row["keyword"]
        rendered = textwrap.indent(
            _render_ortho_view(row, codes, image_types), "    "
        )
        lines.extend([f"    {keyword!r}: {rendered.lstrip()},", ""])
    lines.extend(["}", ""])
    return "\n".join(lines)


def main() -> None:
    """Fetch terminology and regenerate the committed lock module."""
    print("Loading official FHIR terminology...", flush=True)
    codes, image_types, source_versions = load_terminology()
    print(f"  {len(codes)} DICOM codes loaded.")
    print(f"  {len(image_types)} ADA image types loaded.")

    print("Loading views.csv...", flush=True)
    views = load_views()
    print(f"  {len(views)} views loaded.")

    print(f"Generating {OUTPUT}...", flush=True)
    OUTPUT.write_text(
        generate(codes, image_types, views, source_versions), encoding="utf-8"
    )
    print("Done.")


if __name__ == "__main__":
    main()
