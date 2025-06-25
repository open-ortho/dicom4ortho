'''
Unit tests for controller.

@author: Toni Magni

- Ensure the send method actually sends the objects over the network.
- Test that the DICOMs that are received from what comes out of the send method, contain the expected values, specifically the image type, and other types that are set before sending.
- Doesn't mock any dicom4ortho objects, but does not rely on any external DICOM server. So external mocking is performed: a local dimse SCP is set up to receive the DICOMs, and then removed.
- Keep all imports at the top of the file, as per PEP8 guidelines.

'''
import unittest
import logging
import os
import tempfile
import time
from pydicom.dataset import Dataset
from pydicom import dcmread
from pynetdicom import AE, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from dicom4ortho.controller import OrthodonticController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from dicom4ortho.config import VL_DENTAL_VIEW_CID
from pynetdicom.sop_class import VLPhotographicImageStorage # 

SCP_PORT = 7795


class TestDIMSESend(unittest.TestCase):
    """
    Unit tests for OrthodonticController DIMSE send functionality.
    A single local DIMSE SCP is started for all tests in this class.
    """
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                            level=logging.INFO)
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.received_files = []
        def handle_store(event):
            ds = event.dataset
            ds.file_meta = event.file_meta
            out_path = os.path.join(cls.tmpdir.name, f"{ds.SOPInstanceUID}.dcm")
            ds.save_as(out_path, write_like_original=False)
            cls.received_files.append(out_path)
            return 0x0000  # Success
        handlers = [(evt.EVT_C_STORE, handle_store)]
        ae = AE()
        ae.add_supported_context(
            abstract_syntax=VLPhotographicImageStorage,
            transfer_syntax=ALL_TRANSFER_SYNTAXES
        )
        for cx in AllStoragePresentationContexts:
            if cx.abstract_syntax != VLPhotographicImageStorage:
                ae.add_supported_context(cx.abstract_syntax)
        cls.scp = ae.start_server(('127.0.0.1', SCP_PORT), block=False, evt_handlers=handlers, ae_title='TEST-SCP')
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.scp.shutdown()
        cls.tmpdir.cleanup()

    def setUp(self):
        # Clear received files before each test
        self.__class__.received_files.clear()

    def tearDown(self):
        pass

    def test_image_type_code_persists_through_send_dimse(self):
        """
        Test that the DICOM sent via DIMSE contains the expected image type code in ViewCodeSequence.
        Starts a local DIMSE SCP to receive the DICOM, then inspects the received file.
        """

        # Prepare a temp DICOM file
        controller = OrthodonticController()
        metadata = {
            'input_image_filename': 'test/resources/sample_NikonD90.JPG',
            'output_image_filename': 'test/resources/sample_NikonD90.dcm',
            'image_type': 'EV01',
            'patient_firstname': 'Test',
            'patient_lastname': 'Patient',
            'patient_id': '123',
            'patient_sex': 'M',
        }
        photo = controller.convert_image_to_dicom4orthograph(metadata)
        code = Dataset()
        code.CodeValue = 'EV99'
        code.CodingSchemeDesignator = '99OPOR'
        code.CodeMeaning = 'Custom Ortho View'
        OrthodonticPhotograph.set_image_type_code_dataset(
            photo._ds, code, creator_uid='1.2.3.4.5.6.7.8.9')
        photo.save()
        controller.send(
            send_method='dimse',
            dicom_files=[metadata['output_image_filename']],
            pacs_dimse_hostname='127.0.0.1',
            pacs_dimse_port=SCP_PORT,
            pacs_dimse_aet='TEST-SCP',)

        # Wait for the file to be received
        timeout = 5
        waited = 0
        while not self.received_files and waited < timeout:
            time.sleep(0.2)
            waited += 0.2

        self.assertTrue(self.received_files, "No DICOM file received by local DIMSE SCP.")
        ds = dcmread(self.received_files[0])
        found = False
        for item in ds.ViewCodeSequence:
            if (
                getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                getattr(item, 'CodeValue', None) == 'EV99' and
                getattr(item, 'CodingSchemeDesignator', None) == '99OPOR' and
                getattr(item, 'CodeMeaning', None) == 'Custom Ortho View'
            ):
                found = True
        self.assertTrue(found, "Custom image type code not found in ViewCodeSequence after DIMSE send.")
        try:
            os.remove(metadata['output_image_filename'])
        except OSError:
            pass

    @unittest.skip("Not implemented yet")
    def test_image_type_code_series_send_dimse(self):
        """
        Test that sending an OrthodonticSeries via DIMSE results in all received DICOMs containing the expected image type codes in ViewCodeSequence.
        """
        controller = OrthodonticController()
        # Create two OrthodonticPhotograph objects with different codes
        meta1 = {
            'input_image_filename': 'test/resources/sample_NikonD90.JPG',
            'output_image_filename': 'test/resources/sample_NikonD90_1.dcm',
            'image_type': 'EV01',
            'patient_firstname': 'Test',
            'patient_lastname': 'Patient',
            'patient_id': '123',
            'patient_sex': 'M',
        }
        meta2 = {
            'input_image_filename': 'test/resources/sample_NikonD90.JPG',
            'output_image_filename': 'test/resources/sample_NikonD90_2.dcm',
            'image_type': 'EV02',
            'patient_firstname': 'Test2',
            'patient_lastname': 'Patient2',
            'patient_id': '456',
            'patient_sex': 'F',
        }
        photo1 = OrthodonticPhotograph(**meta1)
        code1 = Dataset()
        code1.CodeValue = 'EV99A'
        code1.CodingSchemeDesignator = '99OPOR'
        code1.CodeMeaning = 'Custom Ortho View 1'
        OrthodonticPhotograph.set_image_type_code_dataset(
            photo1._ds, code1, creator_uid='1.2.3.4.5.6.7.8.10')
        photo1.save()
        photo2 = OrthodonticPhotograph(**meta2)
        code2 = Dataset()
        code2.CodeValue = 'EV99B'
        code2.CodingSchemeDesignator = '99OPOR'
        code2.CodeMeaning = 'Custom Ortho View 2'
        OrthodonticPhotograph.set_image_type_code_dataset(
            photo2._ds, code2, creator_uid='1.2.3.4.5.6.7.8.11')
        photo2.save()
        # Build OrthodonticSeries
        from dicom4ortho.m_orthodontic_photograph import OrthodonticSeries
        series = OrthodonticSeries()
        series.add(photo1)
        series.add(photo2)
        # Send series
        controller.send(
            send_method='dimse',
            orthodontic_series=series,
            pacs_dimse_hostname='127.0.0.1',
            pacs_dimse_port=SCP_PORT,
            pacs_dimse_aet='TEST-SCP',)
        # Wait for both files to be received
        timeout = 5
        waited = 0
        while len(self.received_files) < 2 and waited < timeout:
            time.sleep(0.2)
            waited += 0.2
        self.assertEqual(len(self.received_files), 2, "Did not receive both DICOMs via DIMSE.")
        # Check both files
        found1 = found2 = False
        for f in self.received_files:
            ds = dcmread(f)
            for item in ds.ViewCodeSequence:
                if (
                    getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                    getattr(item, 'CodeValue', None) == 'EV99A' and
                    getattr(item, 'CodingSchemeDesignator', None) == '99OPOR' and
                    getattr(item, 'CodeMeaning', None) == 'Custom Ortho View 1'
                ):
                    found1 = True
                if (
                    getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                    getattr(item, 'CodeValue', None) == 'EV99B' and
                    getattr(item, 'CodingSchemeDesignator', None) == '99OPOR' and
                    getattr(item, 'CodeMeaning', None) == 'Custom Ortho View 2'
                ):
                    found2 = True
        self.assertTrue(found1, "Custom image type code 1 not found in ViewCodeSequence after DIMSE send.")
        self.assertTrue(found2, "Custom image type code 2 not found in ViewCodeSequence after DIMSE send.")
        # Cleanup
        for meta in (meta1, meta2):
            try:
                os.remove(meta['output_image_filename'])
            except OSError:
                pass

    def test_image_type_code_dicom_datasets_send_dimse(self):
        """
        Test that sending a list of DICOM datasets via DIMSE results in all received DICOMs containing the expected image type codes in ViewCodeSequence.
        """
        controller = OrthodonticController()
        # Create two OrthodonticPhotograph objects with different codes
        meta1 = {
            'input_image_filename': 'test/resources/sample_NikonD90.JPG',
            'output_image_filename': 'test/resources/sample_NikonD90_1.dcm',
            'image_type': 'EV01',
            'patient_firstname': 'Test',
            'patient_lastname': 'Patient',
            'patient_id': '123',
            'patient_sex': 'M',
        }
        meta2 = {
            'input_image_filename': 'test/resources/sample_NikonD90.JPG',
            'output_image_filename': 'test/resources/sample_NikonD90_2.dcm',
            'image_type': 'EV02',
            'patient_firstname': 'Test2',
            'patient_lastname': 'Patient2',
            'patient_id': '456',
            'patient_sex': 'F',
        }
        photo1 = OrthodonticPhotograph(**meta1)
        code1 = Dataset()
        code1.CodeValue = 'EV99A'
        code1.CodingSchemeDesignator = '99OPOR'
        code1.CodeMeaning = 'Custom Ortho View 1'
        OrthodonticPhotograph.set_image_type_code_dataset(
            photo1._ds, code1, creator_uid='1.2.3.4.5.6.7.8.10')
        photo1.save()
        photo2 = OrthodonticPhotograph(**meta2)
        code2 = Dataset()
        code2.CodeValue = 'EV99B'
        code2.CodingSchemeDesignator = '99OPOR'
        code2.CodeMeaning = 'Custom Ortho View 2'
        OrthodonticPhotograph.set_image_type_code_dataset(
            photo2._ds, code2, creator_uid='1.2.3.4.5.6.7.8.11')
        photo2.save()
        # Prepare dicom_datasets list
        dicom_datasets = [photo1._ds, photo2._ds]
        # Send datasets
        controller.send(
            send_method='dimse',
            dicom_datasets=dicom_datasets,
            pacs_dimse_hostname='127.0.0.1',
            pacs_dimse_port=SCP_PORT,
            pacs_dimse_aet='TEST-SCP',)
        # Wait for both files to be received
        timeout = 5
        waited = 0
        while len(self.received_files) < 2 and waited < timeout:
            time.sleep(0.2)
            waited += 0.2
        self.assertEqual(len(self.received_files), 2, "Did not receive both DICOMs via DIMSE.")
        # Check both files
        found1 = found2 = False
        for f in self.received_files:
            ds = dcmread(f)
            for item in ds.ViewCodeSequence:
                if (
                    getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                    getattr(item, 'CodeValue', None) == 'EV99A' and
                    getattr(item, 'CodingSchemeDesignator', None) == '99OPOR' and
                    getattr(item, 'CodeMeaning', None) == 'Custom Ortho View 1'
                ):
                    found1 = True
                if (
                    getattr(item, 'ContextIdentifier', None) == VL_DENTAL_VIEW_CID and
                    getattr(item, 'CodeValue', None) == 'EV99B' and
                    getattr(item, 'CodingSchemeDesignator', None) == '99OPOR' and
                    getattr(item, 'CodeMeaning', None) == 'Custom Ortho View 2'
                ):
                    found2 = True
        self.assertTrue(found1, "Custom image type code 1 not found in ViewCodeSequence after DIMSE send.")
        self.assertTrue(found2, "Custom image type code 2 not found in ViewCodeSequence after DIMSE send.")
        # Cleanup
        for meta in (meta1, meta2):
            try:
                os.remove(meta['output_image_filename'])
            except OSError:
                pass
