"""Regressions for Apple-only tooling; the existing Python suite is not modified."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import export_terminology as exporter


class TestTerminologyExport(unittest.TestCase):
    """Offline export/check behavior must not change the source lock or hide drift."""

    def test_export_matches_committed_resource_and_source_hash(self):
        rendered = exporter.render()
        self.assertEqual(rendered, exporter.OUTPUT.read_text(encoding="utf-8"))
        payload = json.loads(rendered)
        self.assertEqual(payload["source_lock_sha256"],
                         hashlib.sha256(exporter.SOURCE.read_bytes()).hexdigest())
        self.assertEqual(len(payload["views"]), 73)
        self.assertFalse(any(code["value"] == "AAAAAAA" and code["scheme"] == "DCM"
                             for code in payload["codes"].values()))

    def test_check_detects_swift_drift_without_writing_anything(self):
        source = exporter.SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "terminology.json"
            with mock.patch.object(exporter, "OUTPUT", output):
                with self.assertRaisesRegex(SystemExit, "Swift terminology differs"):
                    exporter.main(["--check"])
                self.assertFalse(output.exists())
                output.write_text(exporter.render(), encoding="utf-8")
                exporter.main(["--check"])
                output.write_text("stale", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "Swift terminology differs"):
                    exporter.main(["--check"])
                self.assertEqual(output.read_text(encoding="utf-8"), "stale")
        self.assertEqual(exporter.SOURCE.read_bytes(), source)

    def test_explicit_export_writes_only_the_swift_destination(self):
        source = exporter.SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "Resources/terminology.json"
            with mock.patch.object(exporter, "OUTPUT", output):
                exporter.main([])
                self.assertEqual(output.read_text(encoding="utf-8"), exporter.render())
        self.assertEqual(exporter.SOURCE.read_bytes(), source)
