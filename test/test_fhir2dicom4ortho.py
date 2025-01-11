import unittest
import json
import os
from fastapi.testclient import TestClient
from fhir2dicom4ortho.fhir_api import fhir_api_app

# Get the directory of the current file
current_dir = os.path.dirname(__file__)

# Construct the path to the JSON file
json_file_path = os.path.join(current_dir, 'fhir2dicom4ortho.Bundle.json')

# Load the test_bundle from the JSON file
with open(json_file_path, 'r') as f:
    test_bundle = json.load(f)

class TestFHIRAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(fhir_api_app)

    def test_handle_bundle(self):
        response = self.client.post("/fhir/Bundle", json=test_bundle)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "draft")

if __name__ == "__main__":
    unittest.main()