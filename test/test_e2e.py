# tests/test_pacs.py
#
# End to End tests, complete processes. These are slow.
#
import fnmatch
import json
import unittest
import io
import os
import warnings
warnings.simplefilter('error', UserWarning)
from logging import DEBUG, INFO

from dicom4ortho import logger
from dicom4ortho.controller import OrthodonticController
from dicom4ortho.__main__ import setup_logging
from dicom4ortho.dicom import wado, dimse
from pathlib import Path
from pydicom import dcmread
from test.test_photography import make_photo_metadata


DEBUG = False

pacs_wado_url = 'http://127.0.0.1:8202/dicom-web/studies'
pacs_wado_username = 'orthanc'
pacs_wado_password = 'mock'
# pacs_wado_url = 'https://ovena-dev.lan.marcorosa.it/dicom-web/studies'
# pacs_wado_username = 'user1'
# pacs_wado_password = '3V2VC4iBMG3UVHz6'
ssl_certificate = None # String of SSL certificate to match. Self-signed certs OK but hostname MUST match, or it will fail.
ssl_verify = False


def compare_jpeg2dicom(jpeg_image_file_path, dicom_image_file_path):
    def extract_jpeg_from_dicom(dicom_path):
        ds = pydicom.dcmread(dicom_path)
        if 'PixelData' in ds:
            # Ensure we're handling JPEG compressed data
            transfer_syntax = ds.file_meta.TransferSyntaxUID
            # JPEG Transfer Syntaxes
            if transfer_syntax.startswith("1.2.840.10008.1.2.4"):
                # Extract the JPEG bytes
                pixel_data_element = ds.PixelData
                start = pixel_data_element.find(
                    b'\xff\xd8')  # Find start of JPEG data
                # Find end of JPEG data starting from the back, to avoid finding FF D9 in Image data.
                end = pixel_data_element.rfind(b'\xff\xd9', start) + 2

                if start != -1 and end != -1:
                    jpeg_bytes = pixel_data_element[start:end]
                    return jpeg_bytes
                else:
                    raise ValueError(
                        "JPEG data not found or incomplete in DICOM.")
        raise ValueError("No appropriate JPEG data found in DICOM file.")

    def are_linearly_related(tuple1, tuple2, tolerance=0.01):
        """
        Checks if the components of two pixel tuples are linearly related within a tolerance.

        Args:
        tuple1 (tuple): The first RGB pixel tuple.
        tuple2 (tuple): The second RGB pixel tuple.
        tolerance (float): The allowable difference in ratios to still be considered linear.

        Returns:
        bool: True if linearly related within tolerance, False otherwise.
        """
        # Prevent division by zero and handle zero case comparisons
        if any(x == 0 for x in tuple1) or any(y == 0 for y in tuple2):
            return False

        # Compute ratios
        ratios = []
        for a, b in zip(tuple1, tuple2):
            if b == 0:  # Prevent division by zero
                return (False, None)
            ratios.append(a / b)

        # Check if ratios are approximately the same
        first_ratio = ratios[0]
        for ratio in ratios[1:]:
            if not (first_ratio - tolerance <= ratio <= first_ratio + tolerance):
                return (False, ratios)

        return (True, ratios)

        # Example usage:
        # tuple1 = (100, 200, 150)
        # tuple2 = (10, 20, 15)
        # print(are_linearly_related(tuple1, tuple2))  # Output should be True if they are linearly related

    # This function should implement the pixel by pixel comparison.
    # Example placeholder logic:
    from PIL import Image
    import pydicom

    # Load JPEG image
    jpeg_img = Image.open(jpeg_image_file_path).convert('RGB')
    jpeg_pixels = jpeg_img.getdata()

    # Extract and load JPEG data from DICOM
    jpeg_bytes_from_dicom = extract_jpeg_from_dicom(dicom_image_file_path)
    logger.info(
        f"\nExtracted {len(jpeg_bytes_from_dicom)} bytes of JPEG data from DICOM.")
    dicom_jpeg_img = Image.open(io.BytesIO(
        jpeg_bytes_from_dicom)).convert('RGB')
    dicom_pixels = dicom_jpeg_img.getdata()

    # Compare each pixel
    if len(jpeg_pixels) != len(dicom_pixels):
        logger.error(
            "\nFAIL: JPEG size [] != DICOM size [{len(dicom_pixels)}]", len(jpeg_pixels))
        return False
    logger.info(
        f"\nPASS size test: both JPEG and DICOM have same size of [{len(dicom_pixels)}].")

    pixel_index = 0
    differences = 0
    for jp, dp in zip(jpeg_pixels, dicom_pixels):
        if jp != dp:
            related, ratios = are_linearly_related(jp, dp)
            if not related:
                if DEBUG:
                    logger.error(
                        f"FAIL: at [{pixel_index}] JPEG pixel is [{jp}], DICOM pixel is [{dp}], ratios: [{ratios}]")
                differences += 1
        else:
            logger.debug(
                f"PASS: at [{pixel_index}] JPEG pixel is [{jp}], DICOM pixel is [{dp}]")
        pixel_index += 1

    if differences == 0:
        return True
    else:
        logger.error(f"FAIL: with [{differences}] different pixels.")
        return False


class TestPacsModule(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        setup_logging(INFO)

    def setUp(self) -> None:
        self.BASE_PATH = os.path.dirname(__file__)
        self.resource_path = Path(self.BASE_PATH) / 'resources'
        return super().setUp()

    def test_full_flow_test_orthodontic_series(self, image_type='IV06'):
        """ Full test, but don't write the DICOM to file.

        Generate DICOM from IMG file into memory and send to PACS. No saved DICOM.

        Uses all images in test/resources/sample_.* and considers them all part of the same series.
        """

        images = self.resource_path.glob('sample_*')
        images = [f for f in images if not fnmatch.fnmatch(f, '*.dcm')]

        c = OrthodonticController()
        o_s = c.convert_images_to_orthodontic_series(
            images, make_photo_metadata())
        o_s.save(filename_prefix='test_e2e')
        response = c.send(
            send_method='wado',
            orthodontic_series=o_s,
            pacs_wado_url=pacs_wado_url,
            pacs_wado_username=pacs_wado_username,
            pacs_wado_password=pacs_wado_password,
            ssl_certificate=ssl_certificate,
            ssl_verify=ssl_verify)

        self.assertEqual(response.status_code, 200, msg=response.reason)
        self.assertTrue(hasattr(response, 'text'))
        logger.info("PASS: response has attribute text.")
        j = json.loads(response.text)
        # DEBUG = True
        logger.debug(json.dumps(j, indent=2))

        # Test that the number of instances in the response matches the number of those sent to pacs.
        instances = j['00081199']['Value']
        self.assertEqual(len(instances), len(o_s))
        logger.info(f"PASS: PACS returned 0008,1199 with {len(instances)}, which is the same amount we sent.")


    def full_flow_test_via_dicom_file(self, inputfile, image_type='IV06'):
        """ Test for each passed file, the entire flow, from JPEG to PACS.

        - Load image from resources/ folder
        - Add image type of image_type, defaults to IV06
        - converts image to dicom, and saves it
        - 
        """

        # 0. Collect data
        metadata = make_photo_metadata()
        metadata['input_image_filename'] = self.resource_path / inputfile
        output_file = (self.resource_path / inputfile).with_suffix('.dcm')
        metadata['output_image_filename'] = output_file
        metadata['image_type'] = image_type

        logger.info(f"[1] Converting {inputfile} to a {output_file}")
        c = OrthodonticController()
        c.convert_image_to_dicom4orthograph_and_save(metadata=metadata)
        # Test existance
        self.assertTrue(output_file.exists())

        logger.info(
            f"[2] Compare the {inputfile} with {output_file}, pixel by pixel, to make sure they are identical. This is slow")
        input_file_extension = Path(inputfile).suffix.lower()
        if input_file_extension == '.jpg' or input_file_extension == '.jpeg':
            self.assertTrue(compare_jpeg2dicom(
                jpeg_image_file_path=metadata["input_image_filename"],
                dicom_image_file_path=output_file))
        else:
            logger.warning(
                f"\nSKIPPING {inputfile} to DICOM comparison, no comparator found.")

        logger.info(f"[3] Verify DICOM File")
        c.validate_dicom_file(output_file)
        
        
        logger.info(f"[4] Test pushing {output_file} to PACS via DIMSE")
        self.send_to_pacs_dimse(output_file)

        logger.info(f"[5] Test pushing {output_file} to PACS via STOW-RS")
        # self.send_to_pacs_wado([output_file])

        logger.info(f"Delete {output_file}")
        try:
            output_file.unlink()
        except FileNotFoundError:
            pass

    def send_to_pacs_dimse(self, dicom_file_path):
        # Arrange
        # dicom_file_path = Path(
        #     '/Users/afm/Desktop/1141_SLOT_1/PAZIENTE_1/DSC_0001.DCM')
        # dicom_file_path = Path('/Users/afm/git/open-ortho/dicom4ortho/test/resources/d90.dcm')
        pacs_dimse_hostname = '127.0.0.1'
        pacs_dimse_port = 4242
        pacs_dimse_aet = 'ORTHANC-MOCK'

        c = OrthodonticController()
        status = c.send(
            send_method='dimse',
            dicom_files=[dicom_file_path],
            pacs_dimse_hostname=pacs_dimse_hostname,
            pacs_dimse_port=pacs_dimse_port,
            pacs_dimse_aet=pacs_dimse_aet)
        self.assertTrue(hasattr(status, 'Status'))
        if status:
            self.assertEqual(status.Status, 0)
        else:
            logger.warning("WARNING: No response from PACS. Skipping test.")

    def send_to_pacs_wado(self, dicom_files=None, orthodontic_series=None):
        # Arrange
        # Act
        c = OrthodonticController()
        response = c.send(
            send_method='wado',
            dicom_files=dicom_files,
            orthodontic_series=orthodontic_series,
            pacs_wado_url=pacs_wado_url,
            pacs_wado_username=pacs_wado_username,
            pacs_wado_password=pacs_wado_password,
            ssl_certificate=ssl_certificate,
            ssl_verify=False)

        self.assertTrue(hasattr(response, 'text'))
        j = json.loads(response.text)

        logger.debug(json.dumps(j, indent=2))

        # Test that the number of instances in the response matches the number of those sent to pacs.
        instances = j['00081199']['Value']
        self.assertEqual(len(instances), len(dicom_files))

        # Loop over the successful instances and assert that they all match with those sent
        for instance, dicom_file in zip(instances, dicom_files):
            dicom_data = dcmread(dicom_file)
            expected_instance_uid = dicom_data.SOPInstanceUID
            expected_study_uid = dicom_data.StudyInstanceUID
            expected_series_uid = dicom_data.SeriesInstanceUID

            self.assertEqual(instance['00081155']['Value'][0],
                             expected_instance_uid, "Instance UID does not match")
            self.assertEqual(j['00081190']['Value'][0].split(
                '/')[-1], expected_study_uid, "Study UID does not match")  # split cuz this in the URL
            # 8,1190 actually has everything, i could just use this.
            self.assertEqual(instance['00081190']['Value'][0].split(
                '/')[-3], expected_series_uid, "Series UID does not match")

            if DEBUG and '00081190' in instance:  # This instance has not been discarded
                url = instance['00081190']['Value'][0]
                logger.debug(url)

        try:
            logger.debug('\nWADO-RS URL of the study:')
            logger.debug(j['00081190']['Value'][0])
        except KeyError:
            logger.error('No instance was uploaded!')

    def test_sample_files(self):
        """ Test with all files in resources/sample_* 

        """
        for sample_file in self.resource_path.glob("sample_*"):
            if Path(sample_file).suffix.lower() == ".dcm":
                continue
            print(f"\nTesting with {sample_file}...")
            self.full_flow_test_via_dicom_file(sample_file)

    def test_send_to_dimse_simple_file(self):
        self.send_to_pacs_dimse(self.resource_path / 'test.dcm')

    def test_send_to_wado_simple_file(self):
        self.send_to_pacs_wado([self.resource_path / 'test.dcm'])


if __name__ == '__main__':
    unittest.main()
