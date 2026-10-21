"""Regressions for DENT-OIP #12's coded request location, distinct from projections."""

from copy import deepcopy
from io import BytesIO
import unittest

from pydicom import dcmread
from pydicom.dataset import Dataset

from dicom4ortho._generated_codes import IMAGE_TYPES, VIEWS
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.photograph_protocols import requested_view_codes
from test.sample_data_generator import make_sample_MWL


def request(codes: list[Dataset], identifier: str = 'request-A') -> Dataset:
    """Build request context, not an alternative implementation of the writer."""
    item = Dataset()
    item.RequestedProcedureID = identifier
    item.ScheduledProcedureStepID = 'step-A'
    item.ScheduledProtocolCodeSequence = codes
    return item


class TestPhotographProtocols(unittest.TestCase):
    """Exercise production creation/getters/setters and their native-dataset boundary."""

    def test_every_view_creates_a_requested_code_and_keeps_one_projection(self):
        for keyword, view in VIEWS.items():
            with self.subTest(keyword=keyword):
                metadata = {'image_type': keyword}
                if keyword in ('IV28', 'IV30', 'EV40'):
                    metadata['view_code_keyword'] = 'projection_right'
                photo = OrthodonticPhotograph(**metadata)
                code = photo._ds.RequestAttributesSequence[0].ScheduledProtocolCodeSequence[0]
                self.assertEqual(code, IMAGE_TYPES[keyword].code.to_dataset())
                self.assertEqual(photo.image_type_code_dataset, code)
                self.assertNotIn('ContextIdentifier', code)
                self.assertNotIn('PerformedProtocolCodeSequence', photo._ds)
                self.assertLessEqual(len(getattr(photo._ds, 'ViewCodeSequence', [])), 1)
                if view.view_code is not None:
                    self.assertEqual(photo._ds.ViewCodeSequence[0].CodeValue, view.view_code.value)

    def test_setter_preserves_requests_unrelated_codes_and_input(self):
        dataset = Dataset()
        unrelated = Dataset()
        unrelated.CodeValue = 'IV01'
        unrelated.CodingSchemeDesignator = '99UNRELATED'
        unrelated.CodeMeaning = 'Not an orthodontic protocol'
        dataset.RequestAttributesSequence = [request([unrelated])]
        dataset.ViewCodeSequence = [VIEWS['EV01'].view_code.to_dataset()]
        original_projection = deepcopy(dataset.ViewCodeSequence)
        code = IMAGE_TYPES['EV01'].code.to_dataset()
        code.CodingSchemeVersion = 'source-version'
        original_code = deepcopy(code)
        OrthodonticPhotograph.set_image_type_code_dataset(dataset, code)
        stored = dataset.RequestAttributesSequence[0]
        self.assertEqual(stored.RequestedProcedureID, 'request-A')
        self.assertEqual(stored.ScheduledProcedureStepID, 'step-A')
        self.assertEqual(stored.ScheduledProtocolCodeSequence, [unrelated, original_code])
        self.assertEqual(dataset.ViewCodeSequence, original_projection)
        self.assertEqual(code, original_code)
        stored.ScheduledProtocolCodeSequence[1].CodeMeaning = 'Edited'
        self.assertEqual(code, original_code)

    def test_multiple_prescriptions_require_explicit_selection(self):
        first = IMAGE_TYPES['EV01'].code.to_dataset()
        second = IMAGE_TYPES['EV02'].code.to_dataset()
        dataset = Dataset()
        dataset.RequestAttributesSequence = [request([first, first, second])]
        before = deepcopy(dataset)
        self.assertIsNone(OrthodonticPhotograph.get_image_type_code_dataset(dataset))
        self.assertEqual(requested_view_codes(dataset), [first, first, second])
        with self.assertRaises(ValueError):
            OrthodonticPhotograph.set_image_type_code_dataset(dataset, second)
        self.assertEqual(dataset, before)
        OrthodonticPhotograph.set_image_type_code_dataset(dataset, second, protocol_index=1)
        self.assertEqual(requested_view_codes(dataset), [first, second, second])

    def test_multiple_requests_require_explicit_selection(self):
        first = IMAGE_TYPES['EV01'].code.to_dataset()
        second = IMAGE_TYPES['EV02'].code.to_dataset()
        dataset = Dataset()
        dataset.RequestAttributesSequence = [request([first]), request([second], 'request-B')]
        before = deepcopy(dataset)
        with self.assertRaises(ValueError):
            OrthodonticPhotograph.set_image_type_code_dataset(dataset, first)
        self.assertEqual(dataset, before)
        OrthodonticPhotograph.set_image_type_code_dataset(dataset, first, request_index=1)
        self.assertEqual(dataset.RequestAttributesSequence[0], before.RequestAttributesSequence[0])
        self.assertEqual(dataset.RequestAttributesSequence[1].RequestedProcedureID, 'request-B')
        self.assertEqual(requested_view_codes(dataset), [first, first])

    def test_unrelated_codes_and_comments_do_not_identify_a_view(self):
        dataset = Dataset()
        code = IMAGE_TYPES['EV01'].code.to_dataset()
        code.CodingSchemeDesignator = '99UNRELATED'
        dataset.RequestAttributesSequence = [request([code])]
        dataset.ImageComments = 'EV01^EV.RP.LR.CO^Extraoral, Right Profile'
        self.assertIsNone(OrthodonticPhotograph.get_image_type_code_dataset(dataset))

    def test_new_request_code_takes_precedence_over_legacy_projection_extension(self):
        dataset = Dataset()
        legacy = IMAGE_TYPES['EV02'].code.to_dataset()
        legacy.ContextIdentifier = '4063'
        legacy.ContextGroupExtensionFlag = 'Y'
        dataset.ViewCodeSequence = [legacy]
        self.assertEqual(OrthodonticPhotograph.get_image_type_code_dataset(dataset), legacy)
        current = IMAGE_TYPES['EV01'].code.to_dataset()
        OrthodonticPhotograph.set_image_type_code_dataset(dataset, current)
        self.assertEqual(OrthodonticPhotograph.get_image_type_code_dataset(dataset), current)
        self.assertEqual(dataset.ViewCodeSequence, [legacy])

    def test_mwl_prescription_survives_creation_and_does_not_become_performed(self):
        worklist = make_sample_MWL('XC', '20261021', '120000')
        codes = [IMAGE_TYPES[key].code.to_dataset() for key in ('EV01', 'EV02', 'EV01')]
        worklist.ScheduledProcedureStepSequence[0].ScheduledProtocolCodeSequence = codes
        procedure = Dataset()
        procedure.CodeValue = 'PROCEDURE'
        procedure.CodingSchemeDesignator = '99TEST'
        procedure.CodeMeaning = 'Requested photographic procedure'
        worklist.RequestedProcedureCodeSequence = [procedure]
        original = deepcopy(worklist)
        photo = OrthodonticPhotograph(dicom_mwl=worklist, image_type='IV01')
        stored = photo._ds.RequestAttributesSequence[0]
        self.assertEqual(stored.ScheduledProtocolCodeSequence, codes)
        self.assertEqual(stored.RequestedProcedureCodeSequence, worklist.RequestedProcedureCodeSequence)
        self.assertEqual(stored.ScheduledProcedureStepID,
                         worklist.ScheduledProcedureStepSequence[0].ScheduledProcedureStepID)
        self.assertIsNone(photo.image_type_code_dataset)
        self.assertNotIn('PerformedProtocolCodeSequence', photo._ds)
        stored.ScheduledProtocolCodeSequence[0].CodeMeaning = 'Edited'
        self.assertEqual(worklist, original)

    def test_serialized_output_retains_the_coded_location(self):
        photo = OrthodonticPhotograph(image_type='EV01')
        stream = BytesIO()
        photo._ds.save_as(stream, write_like_original=False)
        stream.seek(0)
        decoded = dcmread(stream)
        self.assertEqual(decoded.RequestAttributesSequence[0].ScheduledProtocolCodeSequence[0],
                         IMAGE_TYPES['EV01'].code.to_dataset())
        self.assertEqual(len(decoded.ViewCodeSequence), 1)
