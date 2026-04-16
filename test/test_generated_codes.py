"""Tests for the code-generation tool and the generated codes module.

Tests in this file run against the sources (codes.csv, views.csv) and the
generated _generated_codes.py to ensure consistency.
"""

import importlib
import unittest
from pathlib import Path


class TestCodesCsvConsistency(unittest.TestCase):
    """Every keyword referenced in views.csv must exist in codes.csv."""

    def setUp(self):
        # Import lazily so the test can be run before generation too
        from tools.generate_codes import load_codes, load_views
        self.codes = load_codes()
        self.views = load_views()

        # Columns that reference code keywords (single or ^-delimited)
        self.code_columns = [
            "AnatomicRegionSequence",
            "AnatomicRegionModifierSequence",
            "PrimaryAnatomicStructureSequence",
            "PrimaryAnatomicStructureModifierSequence",
            "DeviceSequence",
            "ViewCodeSequence",
            "ViewModifierCodeSequence",
            "AcquisitionContextSequence^OrthognathicFunctionalConditions",
            "AcquisitionContextSequence^FindingByInspection",
            "AcquisitionContextSequence^ObservableEntity",
            "AcquisitionContextSequence^DentalOcclusion",
        ]
        # Columns whose values are resolved as PatientOrientation / ImageLaterality
        self.cs_columns = ["PatientOrientation", "ImageLaterality"]

    def test_all_code_keywords_in_views_exist_in_codes(self):
        """Every keyword referenced in views.csv must be present in codes.csv."""
        missing = []
        for row in self.views:
            for col in self.code_columns:
                cell = row.get(col, "").strip()
                for kw in [k.strip() for k in cell.split("^") if k.strip()]:
                    if kw not in self.codes:
                        missing.append(f"{row['keyword']}.{col}: {kw!r}")
        self.assertEqual(
            missing, [],
            "Keywords in views.csv not found in codes.csv:\n" + "\n".join(missing),
        )

    def test_all_cs_keywords_in_views_exist_in_codes(self):
        """PatientOrientation and ImageLaterality keywords must resolve in codes.csv."""
        missing = []
        for row in self.views:
            for col in self.cs_columns:
                kw = row.get(col, "").strip()
                if kw and kw not in self.codes:
                    missing.append(f"{row['keyword']}.{col}: {kw!r}")
        self.assertEqual(
            missing, [],
            "CS keywords in views.csv not found in codes.csv:\n" + "\n".join(missing),
        )

    def test_no_view_has_unknown_columns(self):
        """All views have the expected columns (no stray/misspelled column names)."""
        if not self.views:
            return
        expected = set(self.views[0].keys())
        for row in self.views:
            self.assertEqual(set(row.keys()), expected)

    def test_all_73_views_present(self):
        """views.csv must contain exactly 73 orthodontic views."""
        self.assertEqual(len(self.views), 73)


class TestGeneratedCodesModule(unittest.TestCase):
    """Tests against the generated _generated_codes.py module."""

    _module = None

    @classmethod
    def setUpClass(cls):
        gen_path = Path(__file__).parent.parent / "dicom4ortho" / "_generated_codes.py"
        if not gen_path.exists():
            raise unittest.SkipTest(
                "_generated_codes.py not found; run: python tools/generate_codes.py"
            )
        cls._module = importlib.import_module("dicom4ortho._generated_codes")

    def test_views_dict_present(self):
        self.assertTrue(hasattr(self._module, "VIEWS"))

    def test_all_73_views_in_dict(self):
        self.assertEqual(len(self._module.VIEWS), 73)

    def test_every_view_is_ortho_view(self):
        from dicom4ortho.m_dent_oip import OrthoView
        for kw, view in self._module.VIEWS.items():
            with self.subTest(view=kw):
                self.assertIsInstance(view, OrthoView)

    def test_dicom_code_to_dataset(self):
        """DicomCode.to_dataset() must return a Dataset with the three required attributes."""
        from dicom4ortho.m_dent_oip import DicomCode
        code = DicomCode(value="123851003", scheme="SCT", meaning="Mouth region structure")
        ds = code.to_dataset()
        self.assertEqual(ds.CodeValue, "123851003")
        self.assertEqual(ds.CodingSchemeDesignator, "SCT")
        self.assertEqual(ds.CodeMeaning, "Mouth region structure")

    def test_views_with_no_patient_orientation(self):
        """IV28 and IV30 must have patient_orientation=None (cannot be determined)."""
        views = self._module.VIEWS
        for kw in ("IV28", "IV30"):
            with self.subTest(view=kw):
                self.assertIsNone(
                    views[kw].patient_orientation,
                    f"{kw} should have patient_orientation=None",
                )

    def test_view_with_multiple_devices(self):
        """IV30 uses device_periodontal_probe; DeviceSequence must be non-empty."""
        view = self._module.VIEWS["IV30"]
        self.assertTrue(len(view.devices) > 0)

    def test_view_with_functional_conditions(self):
        """IV10 has mouth_open; orthognathic_functional_conditions must be non-empty."""
        view = self._module.VIEWS["IV10"]
        self.assertTrue(len(view.orthognathic_functional_conditions) > 0)
        values = [c.value for c in view.orthognathic_functional_conditions]
        self.assertIn("262016004", values)  # mouth_open SNOMED code

    def test_view_modifier_iv28_closeup(self):
        """IV28 uses closeup as a ViewModifier (CID 4065) even though it has no ViewCode.
        The modifier is in view_modifiers but cannot be encoded in DICOM without a parent
        ViewCodeSequence — this is a known data gap for IV28/IV29."""
        view = self._module.VIEWS["IV28"]
        self.assertIsNone(view.view_code)
        values = [c.value for c in view.view_modifiers]
        self.assertIn("789131009", values)  # closeup SNOMED code

    def test_view_dental_occlusion(self):
        """IV01 has centric occlusion; dental_occlusion must be set."""
        view = self._module.VIEWS["IV01"]
        self.assertIsNotNone(view.dental_occlusion)
        self.assertEqual(view.dental_occlusion.value, "110320000")  # co SNOMED code

    def test_no_view_raises_on_to_dataset(self):
        """All DicomCode fields in every view must produce a valid Dataset."""
        from dicom4ortho.m_dent_oip import DicomCode
        for kw, view in self._module.VIEWS.items():
            with self.subTest(view=kw):
                for attr in (
                    "anatomic_region",
                    "anatomic_region_modifier",
                    "primary_anatomic_structure",
                    "primary_anatomic_structure_modifier",
                    "view_code",
                    "dental_occlusion",
                ):
                    code = getattr(view, attr)
                    if code is not None:
                        ds = code.to_dataset()
                        self.assertIsInstance(ds.CodeValue, str)
                for codes in (
                    view.devices,
                    view.view_modifiers,
                    view.orthognathic_functional_conditions,
                    view.findings_by_inspection,
                    view.observable_entities,
                ):
                    for code in codes:
                        ds = code.to_dataset()
                        self.assertIsInstance(ds.CodeValue, str)


class TestApplyView(unittest.TestCase):
    """Tests for OrthodonticPhotograph._apply_view() via the typed VIEWS dict."""

    @classmethod
    def setUpClass(cls):
        gen_path = Path(__file__).parent.parent / "dicom4ortho" / "_generated_codes.py"
        if not gen_path.exists():
            raise unittest.SkipTest(
                "_generated_codes.py not found; run: python tools/generate_codes.py"
            )

    def _make_photo(self, image_type: str, **extra) -> object:
        from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
        return OrthodonticPhotograph(image_type=image_type, **extra)

    def test_all_73_views_produce_non_none_acquisition_context(self):
        """Every view must produce a non-None AcquisitionContextSequence (catches
        the silent keyword-mismatch failures the old string lookup had)."""
        from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
        from dicom4ortho._generated_codes import VIEWS
        for kw in VIEWS:
            with self.subTest(view=kw):
                o = OrthodonticPhotograph(image_type=kw)
                self.assertIsNotNone(
                    getattr(o._ds, 'AcquisitionContextSequence', None),
                    f"{kw}: AcquisitionContextSequence is missing",
                )

    def test_patient_orientation_ev01(self):
        """EV01 should have PatientOrientation set correctly."""
        o = self._make_photo('EV01')
        self.assertEqual(list(o._ds.PatientOrientation), ['A', 'F'])

    def test_patient_orientation_none_for_iv28(self):
        """IV28 has <Can Vary> orientation: PatientOrientation must not be set."""
        o = self._make_photo('IV28')
        # PatientOrientation should be absent or empty when view.patient_orientation is None
        po = getattr(o._ds, 'PatientOrientation', None)
        self.assertTrue(
            po is None or po == [] or po == '',
            f"IV28 PatientOrientation should be unset, got {po!r}",
        )

    def test_anatomic_region_iv01(self):
        """IV01 anatomic region is Mouth (123851003, SCT)."""
        o = self._make_photo('IV01')
        ar = o._ds.AnatomicRegionSequence[0]
        self.assertEqual(ar.CodeValue, '123851003')
        self.assertEqual(ar.CodingSchemeDesignator, 'SCT')

    def test_view_code_ev08(self):
        """EV08 view code is 45-degree projection."""
        o = self._make_photo('EV08')
        vc = o._ds.ViewCodeSequence[0]
        self.assertEqual(vc.CodeValue, '260454004')  # projection_45deg

    def test_view_code_absent_iv28(self):
        """IV28 has no ViewCode (no entry in CID 4062/4063), so ViewCodeSequence must be absent.
        The closeup modifier (CID 4065) cannot be encoded without a parent ViewCode."""
        o = self._make_photo('IV28')
        self.assertIsNone(getattr(o._ds, 'ViewCodeSequence', None))

    def test_device_iv02_mirror(self):
        """IV02 uses a mirror device."""
        o = self._make_photo('IV02')
        devices = o._ds.DeviceSequence
        values = [d.CodeValue for d in devices]
        self.assertIn('47162009', values)  # device_mirror (SCT Mirror, device)

    def test_orthognathic_functional_condition_iv10(self):
        """IV10 has mouth_open as orthognathic functional condition."""
        o = self._make_photo('IV10')
        acs = {
            item.ConceptNameCodeSequence[0].CodeValue: item.ConceptCodeSequence[0].CodeValue
            for item in o._ds.AcquisitionContextSequence
            if hasattr(item, 'ConceptNameCodeSequence')
               and item.ValueType == 'CODE'
               and hasattr(item, 'ConceptCodeSequence')
        }
        # ConceptName for OrthognathicFunctionalConditions is 130325
        self.assertEqual(acs.get('130325'), '262016004')  # mouth_open

    def test_dental_occlusion_iv01(self):
        """IV01 has centric occlusion (co)."""
        o = self._make_photo('IV01')
        acs_by_cn = {
            item.ConceptNameCodeSequence[0].CodeValue: item.ConceptCodeSequence[0].CodeValue
            for item in o._ds.AcquisitionContextSequence
            if hasattr(item, 'ConceptNameCodeSequence')
               and item.ValueType == 'CODE'
               and hasattr(item, 'ConceptCodeSequence')
        }
        # ConceptName for DentalOcclusion is 25272006
        self.assertEqual(acs_by_cn.get('25272006'), '110320000')  # co

    def test_treatment_progress_ev08(self):
        """EV08 with treatment_event_type + days_after_event produces correct ACS items."""
        o = self._make_photo(
            'EV08',
            treatment_event_type='OrthodonticTreatment',
            days_after_event=212,
        )
        numeric_items = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        ]
        self.assertEqual(len(numeric_items), 1)
        self.assertEqual(numeric_items[0].NumericValue, 212)

    def test_set_treatment_progress_updates_acs(self):
        """set_treatment_progress() must update AcquisitionContextSequence."""
        o = self._make_photo('EV08')
        # No progress initially
        numeric_before = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        ]
        self.assertEqual(len(numeric_before), 0)

        o.set_treatment_progress('OrthodonticTreatment', 100)

        numeric_after = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        ]
        self.assertEqual(len(numeric_after), 1)
        self.assertEqual(numeric_after[0].NumericValue, 100)


if __name__ == "__main__":
    unittest.main()
