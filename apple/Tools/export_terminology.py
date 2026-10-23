"""Export Swift's offline resource without changing Python's maintenance pipeline.

This explicit Apple maintenance command reads the committed, reviewed Python lock;
it does not fetch terminology, regenerate that lock, or run during Swift builds.
Python and pydicom are tooling dependencies only, not Swift runtime dependencies.
"""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from dicom4ortho import _generated_codes as lock  # pylint: disable=wrong-import-position

SOURCE = ROOT / "python/dicom4ortho/_generated_codes.py"
OUTPUT = ROOT / "apple/Sources/DICOM4Ortho/Resources/terminology.json"


def render() -> str:
    """Retain exact reviewed values/provenance; do not reinterpret source CSV rows."""
    return json.dumps({
        "schema_version": 1,
        "source_lock_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_provenance": lock.SOURCE_PROVENANCE,
        "codes": {key: asdict(value) for key, value in lock.CODES.items()},
        "image_types": {key: asdict(value) for key, value in lock.IMAGE_TYPES.items()},
        "views": {key: asdict(value) for key, value in lock.VIEWS.items()},
    }, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(arguments: list[str] | None = None) -> None:
    """Check or explicitly write only the Swift resource; Python files stay untouched."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    rendered = render()
    if options.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Swift terminology differs; run python apple/Tools/export_terminology.py")
        print("Swift terminology matches the reviewed Python lock.")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Exported {OUTPUT}")


if __name__ == "__main__":
    main()
