"""Negative and positive oracle cases for Swift's proposed instance representation."""

from copy import deepcopy
import unittest

from pydicom.dataset import Dataset

from validate_outputs import intended_view


def code(value: str, scheme: str, meaning: str) -> Dataset:
    """Create test input only, not a substitute for the production Swift mapper."""
    item = Dataset()
    item.CodeValue = value
    item.CodingSchemeDesignator = scheme
    item.CodeMeaning = meaning
    return item


def instance() -> Dataset:
    """Small standalone metadata fixture for the independent validator's contract."""
    item = Dataset()
    item.ValueType = "CODE"
    item.ConceptNameCodeSequence = [code("AAAAAAA", "DCM", "Intended orthodontic photographic view")]
    item.ConceptCodeSequence = [code("EV01", "99ADA1100", "Extraoral, frontal")]
    dataset = Dataset()
    dataset.AcquisitionContextSequence = [item]
    return dataset


class TestIntendedViewOracle(unittest.TestCase):
    """A valid series prescription must not mask a missing/invalid instance concept."""

    def test_reads_an_instance_intention_without_changing_other_context(self):
        dataset = instance()
        other = deepcopy(dataset.AcquisitionContextSequence[0])
        other.ConceptNameCodeSequence = [code("128741", "DCM", "Longitudinal Temporal Event Type")]
        dataset.AcquisitionContextSequence.append(other)
        before = deepcopy(dataset)
        self.assertEqual(intended_view(dataset).CodeValue, "EV01")
        self.assertEqual(dataset, before)

    def test_request_codes_do_not_identify_the_instance(self):
        dataset = Dataset()
        request = Dataset()
        request.ScheduledProtocolCodeSequence = [code("EV01", "99ADA1100", "Extraoral, frontal")]
        dataset.RequestAttributesSequence = [request]
        with self.assertRaisesRegex(AssertionError, "exactly one intended view"):
            intended_view(dataset)

    def test_rejects_wrong_concept_or_scheme(self):
        for field, value in (("CodeValue", "BBBBBBB"), ("CodingSchemeDesignator", "99OTHER")):
            dataset = instance()
            setattr(dataset.AcquisitionContextSequence[0].ConceptNameCodeSequence[0], field, value)
            with self.subTest(field=field), self.assertRaises(AssertionError):
                intended_view(dataset)

    def test_rejects_duplicate_non_code_and_incomplete_items(self):
        duplicate = instance()
        duplicate.AcquisitionContextSequence.append(deepcopy(duplicate.AcquisitionContextSequence[0]))
        non_code = instance()
        non_code.AcquisitionContextSequence[0].ValueType = "TEXT"
        incomplete = instance()
        del incomplete.AcquisitionContextSequence[0].ConceptCodeSequence[0].CodingSchemeDesignator
        multiple_values = instance()
        values = multiple_values.AcquisitionContextSequence[0].ConceptCodeSequence
        values.append(deepcopy(values[0]))
        for dataset in (duplicate, non_code, incomplete, multiple_values):
            with self.subTest(dataset=dataset), self.assertRaises(AssertionError):
                intended_view(dataset)
