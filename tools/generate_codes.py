#!/usr/bin/env python3
"""Generate dicom4ortho/_generated_codes.py from codes.csv and views.csv.

Reads:
  - codes.csv  via URL_DENT_OIP_CODES  (local file:// by default;
                swap to terminology.open-ortho.org when published)
  - views.csv  via URL_DENT_OIP_VIEWS  (local file:// by default;
                swap to the ADA-1107 published URL when available)

Emits:
  - dicom4ortho/_generated_codes.py  — committed Python module containing
    all DicomCode constants and the VIEWS dict of OrthoView objects.
    This file is the local cache and the lock: no network I/O at runtime.

Usage:
    python tools/generate_codes.py          # from repo root
    make update_resources                   # via Makefile
"""

from __future__ import annotations

import csv
import io
import re
import sys
import textwrap
import urllib.request
from pathlib import Path

# Ensure the package is importable when running from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from dicom4ortho.config import URL_DENT_OIP_CODES, URL_DENT_OIP_VIEWS

OUTPUT = Path(__file__).parent.parent / "dicom4ortho" / "_generated_codes.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_csv(url: str) -> list[dict]:
    """Download a CSV from *url* and return a list of dicts (DictReader rows)."""
    with urllib.request.urlopen(url) as resp:
        text = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def _to_const(keyword: str) -> str:
    """Convert a CSV keyword to a Python UPPER_SNAKE_CASE constant name."""
    # Insert underscore before uppercase letters that follow lowercase/digit
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", keyword)
    # Replace non-alphanumeric characters with underscore
    s = re.sub(r"[^a-zA-Z0-9]", "_", s)
    return s.upper().strip("_")


def _code_repr(keyword: str, codes: dict[str, dict]) -> str:
    """Return the Python constant name for a code keyword, or 'None'."""
    if not keyword:
        return "None"
    if keyword not in codes:
        raise KeyError(f"Unknown code keyword: {keyword!r}")
    return _to_const(keyword)


def _multi_code_repr(cell: str, codes: dict[str, dict]) -> str:
    """Return a tuple literal for a ^-delimited list of code keywords."""
    if not cell:
        return "()"
    parts = [kw.strip() for kw in cell.split("^") if kw.strip()]
    return "(" + ", ".join(_code_repr(kw, codes) for kw in parts) + ",)"


# ---------------------------------------------------------------------------
# Load sources
# ---------------------------------------------------------------------------

def load_codes() -> dict[str, dict]:
    """Return {keyword: {code, scheme, meaning}} from codes.csv."""
    rows = _fetch_csv(URL_DENT_OIP_CODES)
    codes: dict[str, dict] = {}
    for row in rows:
        kw = row.get("keyword", "").strip()
        # Skip meta rows and the placeholder 'na' entry
        if not kw or kw.startswith("__") or kw == "na":
            continue
        codes[kw] = {
            "code": row.get("code", "").strip(),
            "scheme": row.get("codeset", "").strip(),
            "meaning": row.get("meaning", "").strip(),
        }
    return codes


def load_views() -> list[dict]:
    """Return view rows (excluding the VER row) from views.csv."""
    rows = _fetch_csv(URL_DENT_OIP_VIEWS)
    return [r for r in rows if not r["keyword"].startswith("VER:")]


# ---------------------------------------------------------------------------
# Generate source
# ---------------------------------------------------------------------------

def _render_dicom_code_const(keyword: str, info: dict) -> str:
    meaning = info["meaning"].replace('"', '\\"')[:64]
    return (
        f'{_to_const(keyword)} = DicomCode(\n'
        f'    value={info["code"]!r},\n'
        f'    scheme={info["scheme"]!r},\n'
        f'    meaning={meaning!r},\n'
        f')'
    )


def _render_ortho_view(row: dict, codes: dict[str, dict]) -> str:
    """Return a Python expression for one OrthoView."""
    kw = row["keyword"]

    # PatientOrientation: resolve keyword → CS code → split by '^'
    po_kw = row.get("PatientOrientation", "").strip()
    if po_kw:
        po_code = codes[po_kw]["code"]  # e.g. "A^F"
        parts = po_code.split("^")
        patient_orientation = f"({parts[0]!r}, {parts[1]!r})"
    else:
        patient_orientation = "None"

    # ImageLaterality: resolve keyword → single CS letter
    il_kw = row.get("ImageLaterality", "").strip()
    image_laterality = repr(codes[il_kw]["code"]) if il_kw else repr("")

    def opt(col: str) -> str:
        return _code_repr(row.get(col, "").strip(), codes)

    def multi(col: str) -> str:
        return _multi_code_repr(row.get(col, "").strip(), codes)

    desc = row.get("ImageComments", "").strip().replace('"', '\\"')
    series = row.get("SeriesDescription", "").strip().replace('"', '\\"')

    return textwrap.dedent(f"""\
        OrthoView(
            keyword={kw!r},
            patient_orientation={patient_orientation},
            image_laterality={image_laterality},
            anatomic_region={opt('AnatomicRegionSequence')},
            anatomic_region_modifier={opt('AnatomicRegionModifierSequence')},
            primary_anatomic_structure={opt('PrimaryAnatomicStructureSequence')},
            primary_anatomic_structure_modifier={opt('PrimaryAnatomicStructureModifierSequence')},
            devices={multi('DeviceSequence')},
            view_code={opt('ViewCodeSequence')},
            view_modifiers={multi('ViewModifierCodeSequence')},
            orthognathic_functional_conditions={multi('AcquisitionContextSequence^OrthognathicFunctionalConditions')},
            findings_by_inspection={multi('AcquisitionContextSequence^FindingByInspection')},
            observable_entities={multi('AcquisitionContextSequence^ObservableEntity')},
            dental_occlusion={opt('AcquisitionContextSequence^DentalOcclusion')},
            description={desc!r},
            series_description={series!r},
        )""")


def generate(codes: dict[str, dict], views: list[dict]) -> str:
    lines: list[str] = []

    lines.append('"""')
    lines.append("Auto-generated by tools/generate_codes.py — DO NOT EDIT MANUALLY.")
    lines.append("Regenerate with:  python tools/generate_codes.py")
    lines.append('"""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("from dicom4ortho.m_dent_oip import DicomCode, OrthoView")
    lines.append("")
    lines.append("")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("# DicomCode constants (one per row in codes.csv)")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("")

    emitted_consts: set[str] = set()
    for kw, info in codes.items():
        const_name = _to_const(kw)
        if const_name in emitted_consts:
            # Two keywords map to the same constant name (e.g. HeadNeck / head_neck).
            # The CODES dict below will still reference the already-emitted constant.
            continue
        emitted_consts.add(const_name)
        lines.append(_render_dicom_code_const(kw, info))
        lines.append("")

    lines.append("")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("# CODES — keyword → DicomCode lookup (mirrors codes.csv)")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("")
    lines.append("CODES: dict[str, DicomCode] = {")
    for kw in codes:
        lines.append(f"    {kw!r}: {_to_const(kw)},")
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("# VIEWS — all orthodontic views from views.csv")
    lines.append("# -----------------------------------------------------------------------")
    lines.append("")
    lines.append("VIEWS: dict[str, OrthoView] = {")

    for row in views:
        kw = row["keyword"]
        view_expr = _render_ortho_view(row, codes)
        # indent the OrthoView(...) block under its key
        indented = textwrap.indent(view_expr, "    ")
        lines.append(f"    {kw!r}: {indented.lstrip()},")
        lines.append("")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading codes.csv …", flush=True)
    codes = load_codes()
    print(f"  {len(codes)} codes loaded.")

    print("Loading views.csv …", flush=True)
    views = load_views()
    print(f"  {len(views)} views loaded.")

    print(f"Generating {OUTPUT} …", flush=True)
    source = generate(codes, views)
    OUTPUT.write_text(source, encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()
