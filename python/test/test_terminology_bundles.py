"""Guard the Swift offline resource and shared generator without network access."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from dicom4ortho import _generated_codes as lock
from tools import generate_codes as generator


class TestTerminologyBundles(unittest.TestCase):
    """Clinical definitions stay synchronized without coupling language runtimes."""

    def test_bundle_matches_reviewed_python_lock(self):
        if not generator.SWIFT_OUTPUT.exists():
            self.skipTest("Swift checkout resource is not distributed with Python")
        payload = json.loads(generator.SWIFT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(payload["codes"], {key: asdict(value) for key, value in lock.CODES.items()})
        self.assertEqual(payload["image_types"],
                         {key: asdict(value) for key, value in lock.IMAGE_TYPES.items()})
        expected = json.loads(json.dumps({key: asdict(value) for key, value in lock.VIEWS.items()}))
        self.assertEqual(payload["views"], expected)
        self.assertEqual(payload["source_provenance"], lock.SOURCE_PROVENANCE)
        self.assertEqual(payload["source_lock_sha256"],
                         hashlib.sha256(generator.OUTPUT.read_bytes()).hexdigest())

    def test_json_renderer_matches_committed_resource(self):
        if not generator.SWIFT_OUTPUT.exists():
            self.skipTest("Swift checkout resource is not distributed with Python")
        codes = {key: {"code": value.value, "scheme": value.scheme, "meaning": value.meaning}
                 for key, value in lock.CODES.items()}
        image_types = {
            key: {"abbreviation": value.abbreviation, "meaning": value.meaning,
                  "scheme": value.code.scheme, "display": value.code.meaning}
            for key, value in lock.IMAGE_TYPES.items()
        }
        root = Path(__file__).resolve().parents[2]
        views = generator._parse_views(  # pylint: disable=protected-access
            (root / "python/dicom4ortho/resources/views.csv").read_bytes())
        # The packaged CSV predates the reviewed upstream IV29 correction; it is
        # test input, not a replacement maintenance source for the clinical lock.
        next(row for row in views if row["keyword"] == "IV29")["ViewCodeSequence"] = ""
        rendered = generator.generate_json(codes, image_types, views, lock.SOURCE_PROVENANCE,
                                           generator.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(rendered, generator.SWIFT_OUTPUT.read_text(encoding="utf-8"))

    def test_check_mode_validates_every_output_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            python = Path(directory) / "lock.py"
            swift = Path(directory) / "terminology.json"
            python.write_text("python", encoding="utf-8")
            swift.write_text("swift", encoding="utf-8")
            with mock.patch.object(generator, "build_outputs", return_value={python: "python", swift: "swift"}), \
                 mock.patch.object(generator.sys, "argv", ["generate_codes.py", "--check"]):
                generator.main()
                swift.write_text("stale", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "terminology.json.*differs"):
                    generator.main()
                self.assertEqual(swift.read_text(encoding="utf-8"), "stale")
                self.assertEqual(python.read_text(encoding="utf-8"), "python")

    def test_resolution_and_rendering_precede_writes(self):
        with mock.patch.object(generator, "load_terminology", return_value=({}, {}, {})) as load, \
             mock.patch.object(generator, "load_views", return_value=([], {})), \
             mock.patch.object(generator, "generate_json", side_effect=ValueError("bad mapping")), \
             mock.patch.object(generator.sys, "argv", ["generate_codes.py"]), \
             mock.patch.object(Path, "write_text") as write:
            with self.assertRaisesRegex(ValueError, "bad mapping"):
                generator.main()
            load.assert_called_once()
            write.assert_not_called()
