"""Focused behavior/compatibility checks for the structurally annotated subset."""

import inspect
import unittest

from pydicom.dataset import Dataset

from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph


class TestApiCompatibility(unittest.TestCase):
    """Naming overrides must not require changes to existing Python consumers."""

    def test_legacy_constructor_fields_keep_distinct_clinical_roles(self):
        photo = OrthodonticPhotograph(
            patient_firstname="Patient", patient_lastname="Person",
            dental_provider_firstname="Responsible", dental_provider_lastname="Dentist",
            operator_firstname="Acquiring", operator_lastname="Operator",
        )
        dataset = photo.to_dataset()
        self.assertIs(dataset, photo.to_dataset())
        self.assertEqual(str(dataset.PatientName), "Person^Patient")
        self.assertEqual(str(dataset.PhysiciansOfRecord), "Dentist^Responsible")
        self.assertEqual(str(dataset.OperatorsName), "Operator^Acquiring")
        photo.dental_provider_firstname = "Corrected"
        self.assertEqual(str(dataset.PhysiciansOfRecord), "Dentist^Corrected")
        self.assertEqual(str(dataset.OperatorsName), "Operator^Acquiring")

    def test_existing_profile_spelling_and_parameter_default(self):
        signature = inspect.signature(OrthodonticPhotograph.set_dicom_attributes_by_type_keyword)
        self.assertEqual(list(signature.parameters), ["self", "type_keyword"])
        self.assertIsNone(signature.parameters["type_keyword"].default)
        photo = OrthodonticPhotograph()
        self.assertIsNone(photo.set_dicom_attributes_by_type_keyword(type_keyword="EV01"))
        self.assertEqual(photo.type_keyword, "EV01")
        self.assertTrue(photo.is_extraoral())
        self.assertFalse(photo.is_intraoral())

    def test_nullable_code_setter_keeps_existing_noop_contract(self):
        photo = OrthodonticPhotograph()
        code = Dataset()
        code.CodeValue = "example"
        code.CodingSchemeDesignator = "99EXAMPLE"
        code.CodeMeaning = "Example"
        photo.set_image_type_code_dataset(photo.to_dataset(), code, creator_uid="1.2.3")
        self.assertIs(photo.image_type_code_dataset, code)
        photo.image_type_code_dataset = None
        self.assertIs(photo.image_type_code_dataset, code)
        self.assertIsNone(photo.set_image_type_code_dataset(photo.to_dataset(), None))


if __name__ == "__main__":
    unittest.main()
