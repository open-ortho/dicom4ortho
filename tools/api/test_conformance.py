"""Exercise real native declarations and independently mutated unimplemented bodies."""

import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any
import unittest

from check_python import ROOT, annotation_errors, contains_any


class TestStructuralPrototype(unittest.TestCase):
    """A generated contract must reject wrong declarations, not merely match itself."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="d4o-api-tests-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.directory = Path(cls.temporary.name)
        output = cls.directory / "expected"
        subprocess.run([
            "node", str(ROOT / "tools/api/generate.mjs"), "--output", str(output),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.contract = (output / "contract.py").read_text(encoding="utf-8")
        cls.surface = json.loads((output / "surface.json").read_text(encoding="utf-8"))
        cls.probe = (output / "probe.py").read_text(encoding="utf-8").replace(
            "from dicom4ortho.m_orthodontic_photograph import",
            "from fixture_api import",
        )
        scaffold_path = cls.directory / "skeleton.py"
        subprocess.run([
            "node", str(ROOT / "tools/api/generate.mjs"), "--scaffold", str(scaffold_path),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.scaffold = scaffold_path.read_text(encoding="utf-8")

    def check_fixture(self, source):
        """Type check a separate implementation, never call its stubbed members."""
        with tempfile.TemporaryDirectory(prefix="fixture-", dir=self.directory) as directory:
            directory = Path(directory)
            (directory / "contract.py").write_text(self.contract, encoding="utf-8")
            (directory / "probe.py").write_text(self.probe, encoding="utf-8")
            (directory / "fixture_api.py").write_text(source, encoding="utf-8")
            sys.path.insert(0, str(directory))
            sys.modules.pop("fixture_api", None)
            importlib.invalidate_caches()
            try:
                surface = {**self.surface, "target": "fixture_api.OrthodonticPhotograph"}
                errors = annotation_errors(surface)
            finally:
                sys.path.remove(str(directory))
                sys.modules.pop("fixture_api", None)
            env = os.environ.copy()
            env["MYPYPATH"] = str(directory)
            result = subprocess.run([
                sys.executable, "-m", "mypy", "--strict", "--follow-imports=silent",
                "--no-incremental", "--cache-dir=/dev/null", str(directory / "probe.py"),
            ], env=env, capture_output=True, text=True, check=False)
            return errors, result

    def mutated(self, before, after):
        self.assertIn(before, self.scaffold)
        return self.scaffold.replace(before, after, 1)

    def test_actual_python_implementation_passes(self):
        result = subprocess.run([
            sys.executable, str(ROOT / "tools/api/check_python.py"),
        ], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not full API conformance", result.stdout)

    def test_unimplemented_bodies_pass(self):
        errors, result = self.check_fixture(self.scaffold)
        self.assertEqual(errors, [])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("raise NotImplementedError", self.scaffold)

    def test_missing_or_wrong_method_name_fails(self):
        source = self.mutated("def is_extraoral(", "def not_the_required_name(")
        errors, result = self.check_fixture(source)
        self.assertIn("is_extraoral: missing member", errors)
        self.assertNotEqual(result.returncode, 0)

    def test_wrong_return_type_fails(self):
        source = self.mutated("def is_intraoral(self) -> bool:", "def is_intraoral(self) -> str:")
        errors, result = self.check_fixture(source)
        self.assertEqual(errors, [])
        self.assertNotEqual(result.returncode, 0)

    def test_wrong_parameter_type_fails(self):
        source = self.mutated("def set_view_code(self, keyword: str)",
                              "def set_view_code(self, keyword: int)")
        _, result = self.check_fixture(source)
        self.assertNotEqual(result.returncode, 0)

    def test_wrong_parameter_name_fails(self):
        source = self.mutated("def set_view_code(self, keyword: str)",
                              "def set_view_code(self, wrong_keyword: str)")
        _, result = self.check_fixture(source)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_setter_fails(self):
        source = self.mutated(
            "    @patient_firstname.setter\n"
            "    def patient_firstname(self, value: str) -> None:\n"
            "        raise NotImplementedError\n", "",
        )
        errors, result = self.check_fixture(source)
        self.assertIn("patient_firstname: missing accessor/callable", errors)
        self.assertNotEqual(result.returncode, 0)

    def test_restricting_nullable_setter_fails(self):
        source = self.mutated("def image_type_code_dataset(self, value: _NativeDataset | None)",
                              "def image_type_code_dataset(self, value: _NativeDataset)")
        _, result = self.check_fixture(source)
        self.assertNotEqual(result.returncode, 0)

    def test_static_changed_to_instance_fails(self):
        source = self.mutated(
            "@staticmethod\n    def get_image_type_code_dataset(ds:",
            "def get_image_type_code_dataset(self, ds:",
        )
        errors, _ = self.check_fixture(source)
        self.assertIn("get_image_type_code_dataset: static/instance method mismatch", errors)

    def test_missing_annotation_is_not_verified(self):
        source = self.mutated("def is_extraoral(self) -> bool:", "def is_extraoral(self):")
        errors, _ = self.check_fixture(source)
        self.assertIn("is_extraoral.return: unverified annotation (missing or Any)", errors)

    def test_any_annotation_is_not_verified(self):
        source = self.mutated("def is_extraoral(self) -> bool:", "def is_extraoral(self) -> Any:")
        source = source.replace("from typing import Protocol", "from typing import Any, Protocol")
        errors, _ = self.check_fixture(source)
        self.assertIn("is_extraoral.return: unverified annotation (missing or Any)", errors)

    def test_changed_default_fails(self):
        source = self.mutated('creator_uid: str | None = None',
                              'creator_uid: str | None = "not-the-default"')
        errors, _ = self.check_fixture(source)
        self.assertIn(
            "set_image_type_code_dataset.creator_uid: expected explicit None default", errors,
        )

    def test_required_argument_cannot_replace_optional(self):
        source = self.mutated("type_keyword: str | None = None", "type_keyword: str | None")
        errors, result = self.check_fixture(source)
        self.assertIn(
            "set_dicom_attributes_by_type_keyword.type_keyword: expected explicit None default",
            errors,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_nested_any_is_unverified(self):
        self.assertTrue(contains_any(list[Any]))
        self.assertFalse(contains_any(list[str | None]))

    def generate_custom(self, *, spec=None, binding=None, expected_contract=None):
        with tempfile.TemporaryDirectory(prefix="generate-", dir=self.directory) as directory:
            directory = Path(directory)
            spec_path = ROOT / "api/dicom4ortho.webidl"
            binding_path = ROOT / "python/api-bindings.json"
            if spec is not None:
                spec_path = directory / "test.webidl"
                spec_path.write_text(spec, encoding="utf-8")
            if binding is not None:
                binding_path = directory / "binding.json"
                binding_path.write_text(json.dumps(binding), encoding="utf-8")
            result = subprocess.run([
                "node", str(ROOT / "tools/api/generate.mjs"), "--spec", str(spec_path),
                "--bindings", str(binding_path), "--output", str(directory / "out"),
            ], cwd=ROOT, capture_output=True, text=True, check=False)
            if expected_contract is not None:
                self.assertEqual(result.returncode, 0, result.stderr)
                contract = (directory / "out/contract.py").read_text(encoding="utf-8")
                self.assertIn(expected_contract, contract)
            return result

    def test_unknown_member_override_fails(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["overrides"]["nonexistentMember"] = {"name": "anything"}
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown overridden member", result.stderr)

    def test_binding_cannot_override_a_required_type(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["overrides"]["patientFirstName"]["type"] = "int"
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown override key", result.stderr)

    def test_unknown_parameter_override_fails(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["overrides"]["applyProfile"]["parameters"] = {"noSuchParameter": "name"}
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown parameter", result.stderr)

    def test_name_collision_fails(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["overrides"]["patientLastName"]["name"] = "patient_firstname"
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Binding name collision", result.stderr)

    def test_unmapped_native_type_fails(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["nativeTypes"] = {}
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unmapped native type", result.stderr)

    def test_unsupported_selected_construct_fails(self):
        spec = ('interface OrthodonticPhotograph { '
                '[StructuralPrototype] sequence<DOMString> list(); };')
        binding = {"formatVersion": 1, "interface": "OrthodonticPhotograph",
                   "target": "fixture_api.OrthodonticPhotograph"}
        result = self.generate_custom(spec=spec, binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not emit generics/unions", result.stderr)

    def test_empty_selection_fails(self):
        binding = {"formatVersion": 1, "interface": "OrthodonticPhotograph",
                   "target": "fixture_api.OrthodonticPhotograph"}
        result = self.generate_custom(spec="interface OrthodonticPhotograph {};", binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing an empty check", result.stderr)

    def test_acronym_casing_is_deterministic(self):
        spec = ('interface OrthodonticPhotograph { '
                '[StructuralPrototype] undefined assignUID(DOMString creatorUID); };')
        binding = {"formatVersion": 1, "interface": "OrthodonticPhotograph",
                   "target": "fixture_api.OrthodonticPhotograph"}
        result = self.generate_custom(
            spec=spec, binding=binding,
            expected_contract="def assign_uid(self, creator_uid: str) -> None",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reserved_native_name_requires_override(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["overrides"]["patientFirstName"]["name"] = "class"
        result = self.generate_custom(binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python keyword requires a binding override", result.stderr)

    def test_unknown_selected_modifier_is_not_silently_ignored(self):
        spec = ('interface OrthodonticPhotograph { '
                '[StructuralPrototype, UnknownModifier] boolean isReady(); };')
        binding = {"formatVersion": 1, "interface": "OrthodonticPhotograph",
                   "target": "fixture_api.OrthodonticPhotograph"}
        result = self.generate_custom(spec=spec, binding=binding)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported selected declaration", result.stderr)

    def test_invalid_idl_syntax_fails(self):
        result = self.generate_custom(spec="interface MissingBraces;")
        self.assertNotEqual(result.returncode, 0)

    def test_scaffold_uses_the_bound_native_type_name(self):
        binding = json.loads((ROOT / "python/api-bindings.json").read_text(encoding="utf-8"))
        binding["target"] = "future_port.NativePhoto"
        binding_path = self.directory / "native-binding.json"
        binding_path.write_text(json.dumps(binding), encoding="utf-8")
        scaffold_path = self.directory / "native-photo.py"
        result = subprocess.run([
            "node", str(ROOT / "tools/api/generate.mjs"), "--bindings", str(binding_path),
            "--scaffold", str(scaffold_path),
        ], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        scaffold = scaffold_path.read_text(encoding="utf-8")
        self.assertIn("class NativePhoto:", scaffold)
        self.assertIn("def patient_firstname(", scaffold)

    def test_scaffolding_does_not_overwrite_human_code(self):
        destination = self.directory / "human.py"
        destination.write_text("# keep my implementation\n", encoding="utf-8")
        result = subprocess.run([
            "node", str(ROOT / "tools/api/generate.mjs"), "--scaffold", str(destination),
        ], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_text(encoding="utf-8"), "# keep my implementation\n")


if __name__ == "__main__":
    unittest.main()
