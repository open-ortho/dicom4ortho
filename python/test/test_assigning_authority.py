"""Contract tests for the public Patient ID assigning-authority helper."""
import copy
import io
import unittest

from pydicom import dcmread, dcmwrite
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage

from dicom4ortho import set_patient_id_assigning_authority


class TestAssigningAuthority(unittest.TestCase):
    """Validate before mutation and replace, rather than accumulate, qualifiers."""

    def setUp(self):
        self.dataset = Dataset()
        self.dataset.PatientID = "P123"
        self.root = "1.3.6.1.4.1.62074.1.4.4"

    def apply(self, instance=123, root=None, label="TOPS-PRACTICE-123"):
        """Invoke the public API with overridable inputs."""
        set_patient_id_assigning_authority(
            self.dataset, label, self.root if root is None else root, instance)

    def test_complete_identity_and_replacement(self):
        self.dataset.IssuerOfPatientIDQualifiersSequence = [Dataset(), Dataset()]
        for instance in (123, "123", "000123"):
            self.apply(instance)
            self.assertEqual(self.dataset.PatientID, "P123")
            self.assertEqual(self.dataset.IssuerOfPatientID, "TOPS-PRACTICE-123")
            self.assertEqual(len(self.dataset.IssuerOfPatientIDQualifiersSequence), 1)
            qualifier = self.dataset.IssuerOfPatientIDQualifiersSequence[0]
            self.assertEqual(qualifier.LocalNamespaceEntityID, "TOPS-PRACTICE-123")
            self.assertEqual(qualifier.UniversalEntityID, f"{self.root}.123")
            self.assertEqual(qualifier.UniversalEntityIDType, "ISO")
        self.assertFalse(any(element.tag.is_private for element in self.dataset.iterall()))

    def test_zero_is_a_valid_generic_oid_component(self):
        self.apply("000")
        self.assertEqual(self.dataset.IssuerOfPatientIDQualifiersSequence[0].UniversalEntityID,
                         f"{self.root}.0")

    def test_other_application_root_and_label(self):
        self.apply(42, root="2.999.1", label="OTHER-APP")
        self.assertEqual(self.dataset.IssuerOfPatientID, "OTHER-APP")
        self.assertEqual(self.dataset.IssuerOfPatientIDQualifiersSequence[0].UniversalEntityID,
                         "2.999.1.42")

    def test_invalid_instances_leave_dataset_unchanged(self):
        self.apply()
        before = copy.deepcopy(self.dataset)
        for instance in (None, -1, "-1", "", " ", "+1", "1.0", 1.0, True, False,
                         "1e3", "1.2", "1\\2", "１２", "1\n", " 1", b"1", "9" * 65):
            with self.subTest(instance=instance), self.assertRaises(ValueError):
                self.apply(instance)
            self.assertEqual(self.dataset, before)

    def test_invalid_roots(self):
        for root in ("", "1", "3.1", "1.40", "0.40", "1.02", "1..2", "1.2.",
                     ".1.2", "1.2a", "1.2\n", " 1.2", "1.-2", "1.２", "1." + "9" * 63):
            with self.subTest(root=root), self.assertRaises(ValueError):
                self.apply(root=root)
        with self.assertRaises(ValueError):
            set_patient_id_assigning_authority(self.dataset, "LOCAL", None, 1)

    def test_invalid_local_labels(self):
        for label in (None, "", " ", "x" * 65, "A\\B", "A\nB", "A\0B", "A\x7fB", " A", "A "):
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.apply(label=label)

    def test_uid_length_boundary(self):
        root = "2." + "1" * 60
        self.apply(1, root=root, label="x" * 64)
        self.assertEqual(len(self.dataset.IssuerOfPatientIDQualifiersSequence[0].UniversalEntityID),
                         64)
        with self.assertRaises(ValueError):
            self.apply(10, root=root)

    def test_dicom_round_trip(self):
        self.apply()
        self.dataset.SOPClassUID = SecondaryCaptureImageStorage
        self.dataset.SOPInstanceUID = "2.25.123"
        self.dataset.file_meta = FileMetaDataset()
        self.dataset.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        buffer = io.BytesIO()
        dcmwrite(buffer, self.dataset, enforce_file_format=True)
        buffer.seek(0)
        restored = dcmread(buffer)
        self.assertEqual(restored.IssuerOfPatientIDQualifiersSequence,
                         self.dataset.IssuerOfPatientIDQualifiersSequence)
