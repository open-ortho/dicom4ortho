"""Tests for official terminology bindings and the generated codes module."""

import importlib
import unittest
import warnings
from datetime import date, datetime
from pathlib import Path


class TestTerminologySourceConsistency(unittest.TestCase):
    """Every local view binding must resolve through a declared source."""

    def setUp(self):
        from tools.generate_codes import CODE_BINDINGS, LOCAL_CODES, load_views
        self.codes = set(CODE_BINDINGS) | set(LOCAL_CODES)
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
        """Every terminology keyword in views.csv must have a source binding."""
        missing = []
        for row in self.views:
            for col in self.code_columns:
                cell = row.get(col, "").strip()
                for kw in [k.strip() for k in cell.split("^") if k.strip()]:
                    if kw not in self.codes:
                        missing.append(f"{row['keyword']}.{col}: {kw!r}")
        self.assertEqual(
            missing, [],
            "Keywords in views.csv without terminology bindings:\n" + "\n".join(missing),
        )

    def test_all_cs_keywords_in_views_exist_in_codes(self):
        """PatientOrientation and ImageLaterality keywords must resolve locally."""
        missing = []
        for row in self.views:
            for col in self.cs_columns:
                kw = row.get(col, "").strip()
                if kw and kw not in self.codes:
                    missing.append(f"{row['keyword']}.{col}: {kw!r}")
        self.assertEqual(
            missing, [],
            "CS keywords in views.csv without bindings:\n" + "\n".join(missing),
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

    def test_cid_4070_bindings_use_canonical_sct_codes(self):
        """Treatment progress bindings select only the intended SCT concepts."""
        from tools.generate_codes import CODE_BINDINGS, SCT_SYSTEM
        expected = {
            "PatientRegistration": "184047000",
            "OrthodonticTreatmentStarted": "1332161000",
            "OrthodonticTreatmentStopped": "1340210007",
        }
        for keyword, code in expected.items():
            with self.subTest(keyword=keyword):
                binding = CODE_BINDINGS[keyword]
                self.assertEqual(binding.source, "CID4070")
                self.assertEqual(binding.system, SCT_SYSTEM)
                self.assertEqual(binding.code, code)

    def test_dcm_concept_names_use_official_code_system(self):
        from tools.generate_codes import CODE_BINDINGS, DCM_SYSTEM
        expected = {
            "OrthognathicFunctionalConditions": "130325",
            "TemporalEventType": "128741",
            "OffsetFromEvent": "128740",
        }
        for keyword, code in expected.items():
            with self.subTest(keyword=keyword):
                binding = CODE_BINDINGS[keyword]
                self.assertEqual(binding.source, "DCM_CODE_SYSTEM")
                self.assertEqual(binding.system, DCM_SYSTEM)
                self.assertEqual(binding.code, code)

    def test_known_fhir_display_error_uses_normative_dicom_meaning(self):
        from dicom4ortho._generated_codes import CODES
        from tools.generate_codes import CODE_BINDINGS, CODE_MEANING_OVERRIDES, SCT_SYSTEM
        binding = CODE_BINDINGS["frenum"]
        self.assertEqual(binding.source, "CID4061")
        self.assertEqual(binding.system, SCT_SYSTEM)
        self.assertEqual(binding.code, "7652006")
        self.assertEqual(
            CODE_MEANING_OVERRIDES[(binding.source, binding.system, binding.code)],
            "Frenulum labii",
        )
        self.assertEqual(CODES["frenum"].meaning, "Frenulum labii")


class TestFhirResolution(unittest.TestCase):
    """FHIR resolution must not confuse primary codes with mapping identifiers."""

    def test_resolve_code_selects_system_and_code(self):
        from tools.generate_codes import CodeBinding, SCT_SYSTEM, resolve_code
        resource = {
            "resourceType": "ValueSet",
            "compose": {"include": [
                {"system": "http://snomed.info/srt", "concept": [
                    {"code": "P0-0081C", "display": "Patient registration"},
                ]},
                {"system": SCT_SYSTEM, "concept": [
                    {"code": "184047000", "display": "Patient registration"},
                ]},
            ]},
        }
        code = resolve_code(
            resource, CodeBinding("CID4070", SCT_SYSTEM, "184047000")
        )
        self.assertEqual(code, {
            "code": "184047000",
            "scheme": "SCT",
            "meaning": "Patient registration",
        })

    def test_resolve_code_rejects_missing_code(self):
        from tools.generate_codes import CodeBinding, SCT_SYSTEM, resolve_code
        resource = {"resourceType": "ValueSet", "compose": {"include": []}}
        with self.assertRaisesRegex(ValueError, "found 0"):
            resolve_code(resource, CodeBinding("CID4070", SCT_SYSTEM, "missing"))

    def test_resolve_code_rejects_filter_based_value_set(self):
        from tools.generate_codes import CodeBinding, SCT_SYSTEM, resolve_code
        resource = {
            "resourceType": "ValueSet",
            "compose": {"include": [{
                "system": SCT_SYSTEM,
                "filter": [{"property": "concept", "op": "is-a", "value": "123"}],
            }]},
        }
        with self.assertRaisesRegex(ValueError, "Filter-based"):
            resolve_code(resource, CodeBinding("CID4070", SCT_SYSTEM, "123"))


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

    def test_source_versions_present(self):
        self.assertIn("DCM_CODE_SYSTEM", self._module.SOURCE_VERSIONS)
        self.assertIn("CID4070", self._module.SOURCE_VERSIONS)
        self.assertIn("ADA_INTRAORAL_2D", self._module.SOURCE_VERSIONS)

    def test_all_73_ada_image_types_present(self):
        self.assertEqual(len(self._module.IMAGE_TYPES), 73)
        self.assertEqual(self._module.IMAGE_TYPES["EV01"].abbreviation, "EO.RP.LR.CO")

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
        the silent keyword-mismatch failures the old string lookup had).
        Incomplete views (variable ViewCode) are constructed with a view_code_keyword."""
        from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
        from dicom4ortho._generated_codes import VIEWS
        for kw in VIEWS:
            with self.subTest(view=kw):
                view = VIEWS[kw]
                kwargs = {'image_type': kw}
                if view.view_code is None:
                    kwargs['view_code_keyword'] = 'projection_right'
                o = OrthodonticPhotograph(**kwargs)
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
        o = self._make_photo('IV28', view_code_keyword='projection_right')
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

    def test_incomplete_view_raises_without_view_code(self):
        """IV28, IV30, and EV40 have variable ViewCode: constructing without
        view_code_keyword must raise TypeError immediately."""
        from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
        for kw in ('IV28', 'IV30', 'EV40'):
            with self.subTest(view=kw):
                with self.assertRaises(TypeError):
                    OrthodonticPhotograph(image_type=kw)

    def test_complete_view_needs_no_view_code(self):
        """Complete views must construct without view_code_keyword."""
        o = self._make_photo('EV01')
        self.assertIsNotNone(o)

    def test_view_code_keyword_sets_view_code_with_modifier(self):
        """IV28 + view_code_keyword attaches closeup modifier to the ViewCode."""
        o = self._make_photo('IV28', view_code_keyword='projection_right')
        vc = o._ds.ViewCodeSequence[0]
        self.assertEqual(vc.CodeValue, '399198007')  # projection_right
        modifiers = vc.ViewModifierCodeSequence
        values = [m.CodeValue for m in modifiers]
        self.assertIn('789131009', values)  # closeup

    def test_view_code_keyword_no_modifiers_iv30(self):
        """IV30 has no view modifiers: ViewCodeSequence set, no ViewModifierCodeSequence."""
        o = self._make_photo('IV30', view_code_keyword='projection_right')
        vc = o._ds.ViewCodeSequence[0]
        self.assertEqual(vc.CodeValue, '399198007')  # projection_right
        self.assertFalse(hasattr(vc, 'ViewModifierCodeSequence'))

    def test_set_view_code_replaces_existing(self):
        """set_view_code() replaces ViewCodeSequence; modifiers re-attached for IV28."""
        o = self._make_photo('IV28', view_code_keyword='projection_right')
        o.set_view_code('projection_frontal')
        vc = o._ds.ViewCodeSequence[0]
        self.assertEqual(vc.CodeValue, '399033003')  # projection_frontal
        values = [m.CodeValue for m in vc.ViewModifierCodeSequence]
        self.assertIn('789131009', values)  # closeup still attached

    def test_device_iv02_mirror(self):
        """IV02 uses the CID 4072 intraoral photography mirror."""
        o = self._make_photo('IV02')
        devices = o._ds.DeviceSequence
        values = [d.CodeValue for d in devices]
        self.assertIn('1332162007', values)

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
        """Each ADA 1100 phase emits its canonical CID 4070 event and offset."""
        expected = {
            'PatientRegistration': ('184047000', 'Patient registration'),
            'OrthodonticTreatmentStarted': (
                '1332161000', 'Orthodontic Treatment started'),
            'OrthodonticTreatmentStopped': (
                '1340210007', 'Orthodontic Treatment stopped'),
        }
        for event_type, (code, meaning) in expected.items():
            with self.subTest(event_type=event_type):
                o = self._make_photo(
                    'EV08',
                    acquisition_datetime=datetime(2026, 7, 14, 10, 30),
                    treatment_event_type=event_type,
                    treatment_event_date=date(2026, 7, 1),
                )
                event_items = [
                    item for item in o._ds.AcquisitionContextSequence
                    if item.ValueType == 'CODE'
                    and item.ConceptNameCodeSequence[0].CodeValue == '128741'
                ]
                numeric_items = [
                    item for item in o._ds.AcquisitionContextSequence
                    if item.ValueType == 'NUMERIC'
                ]
                self.assertEqual(len(event_items), 1)
                self.assertEqual(event_items[0].ConceptCodeSequence[0].CodeValue, code)
                self.assertEqual(
                    event_items[0].ConceptCodeSequence[0].CodingSchemeDesignator, 'SCT')
                self.assertEqual(
                    event_items[0].ConceptCodeSequence[0].CodeMeaning, meaning)
                self.assertEqual(len(numeric_items), 1)
                self.assertEqual(numeric_items[0].NumericValue, 13)
                self.assertEqual(
                    numeric_items[0].ConceptNameCodeSequence[0].CodeValue, '128740')
                units = numeric_items[0].MeasurementUnitsCodeSequence[0]
                self.assertEqual((units.CodeValue, units.CodingSchemeDesignator), ('d', 'UCUM'))
                self.assertEqual(units.CodeMeaning, 'days')

    def test_set_treatment_progress_updates_acs(self):
        """The deprecated days API remains functional and warns callers."""
        o = self._make_photo('EV08')
        # No progress initially
        numeric_before = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        ]
        self.assertEqual(len(numeric_before), 0)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            o.set_treatment_progress('OrthodonticTreatment', 100)

        numeric_after = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        ]
        self.assertEqual(len(numeric_after), 1)
        self.assertEqual(numeric_after[0].NumericValue, 100)
        messages = [str(warning.message) for warning in caught]
        self.assertTrue(any('set_treatment_progress' in message for message in messages))
        self.assertTrue(any('OrthodonticTreatmentStarted' in message for message in messages))
        event_item = next(
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'CODE'
            and item.ConceptNameCodeSequence[0].CodeValue == '128741'
        )
        self.assertEqual(event_item.ConceptCodeSequence[0].CodeValue, '1332161000')

    def test_legacy_posttreatment_metadata_warns_and_maps_to_stopped(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            o = self._make_photo(
                'EV08', treatment_event_type='Posttreatment', days_after_event='12')
        messages = [str(warning.message) for warning in caught]
        self.assertTrue(any('days_after_event' in message for message in messages))
        self.assertTrue(any('OrthodonticTreatmentStopped' in message for message in messages))
        event_item = next(
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'CODE'
            and item.ConceptNameCodeSequence[0].CodeValue == '128741'
        )
        self.assertEqual(event_item.ConceptCodeSequence[0].CodeValue, '1340210007')

    def test_set_treatment_progress_from_date_uses_dataset_acquisition_date(self):
        o = self._make_photo('EV08')
        o.set_time_captured(datetime(2026, 7, 14, 10, 30))
        o.set_treatment_progress_from_date('PatientRegistration', date(2026, 7, 1))
        numeric = next(
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        )
        self.assertEqual(numeric.NumericValue, 13)

    def test_zero_day_offset_is_valid(self):
        o = self._make_photo('EV08')
        o.set_treatment_progress_from_date(
            'OrthodonticTreatmentStarted', '2026-07-14', '2026-07-14')
        numeric = next(
            item for item in o._ds.AcquisitionContextSequence
            if item.ValueType == 'NUMERIC'
        )
        self.assertEqual(numeric.NumericValue, 0)

    def test_event_date_after_acquisition_is_rejected(self):
        o = self._make_photo('EV08')
        with self.assertRaisesRegex(ValueError, 'cannot be after'):
            o.set_treatment_progress_from_date(
                'PatientRegistration', '2026-07-15', '2026-07-14')

    def test_event_date_requires_acquisition_date(self):
        o = self._make_photo('EV08')
        with self.assertRaisesRegex(ValueError, 'acquisition date is required'):
            o.set_treatment_progress_from_date('PatientRegistration', '2026-07-01')

    def test_unknown_treatment_event_is_rejected(self):
        o = self._make_photo('EV08')
        with self.assertRaisesRegex(ValueError, 'Unknown treatment event type'):
            o.set_treatment_progress_from_date('Unknown', '2026-07-01', '2026-07-14')

    def test_blank_progress_metadata_is_ignored(self):
        o = self._make_photo(
            'EV08',
            acquisition_datetime=' ',
            treatment_event_type='',
            treatment_event_date=' ',
            days_after_event='',
        )
        progress = [
            item for item in o._ds.AcquisitionContextSequence
            if item.ConceptNameCodeSequence[0].CodeValue in ('128740', '128741')
        ]
        self.assertEqual(progress, [])

    def test_partial_progress_metadata_is_rejected(self):
        cases = [
            {'treatment_event_type': 'PatientRegistration'},
            {'treatment_event_date': '2026-07-01'},
            {'days_after_event': 12},
        ]
        for metadata in cases:
            with self.subTest(metadata=metadata):
                with self.assertRaisesRegex(ValueError, 'required'):
                    self._make_photo('EV08', **metadata)


if __name__ == "__main__":
    unittest.main()
