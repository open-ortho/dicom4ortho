import os

os.environ['F2D4O_VERBOSITY'] = '2'
os.environ['F2D4O_FHIR_LISTEN'] = ''
os.environ['F2D4O_FHIR_PORT'] = '8123'
os.environ['F2D4O_PACS_SEND_METHOD'] = 'dimse'
os.environ['F2D4O_PACS_DIMSE_AET'] = 'ORTHANC-MOCK'
os.environ['F2D4O_PACS_DIMSE_IP'] = '127.0.0.1'
os.environ['F2D4O_PACS_DIMSE_PORT'] = '4242'

import unittest
import json
from time import sleep
from fastapi.testclient import TestClient
from fhir.resources.bundle import Bundle
from fhir2dicom4ortho.fhir_api import fhir_api_app
from fhir2dicom4ortho.tasks import process_bundle, TASK_DRAFT, TASK_COMPLETED, TASK_FAILED, TASK_REJECTED, TASK_INPROGRESS
from fhir2dicom4ortho.task_store import TaskStore 

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
        print("********** Waiting for Task to Complete... **********")
        sleep(1)
        response = self.client.get(f"/fhir/Task/{response_data['id']}")
        response_data = response.json()
        self.assertEqual(response_data["status"], "completed")


class TestTasks(unittest.TestCase):
    def setUp(self):
        self.task_store = TaskStore(db_url='sqlite:///test_tasks.sqlite')
        self.bundle = Bundle.model_validate(test_bundle)

    def test_process_bundle_task(self):
        """ Test requires mock PACS server """
        task_id = self.task_store.reserve_id(description="Test Task")
        # Capture the log output
        with self.assertLogs('pynetdicom._handlers', level='INFO') as log:
            process_bundle(self.bundle, task_id, self.task_store)

        task = self.task_store.get_fhir_task_by_id(task_id)
        self.assertIsNotNone(task)
        self.assertIn(task.status, [TASK_COMPLETED, TASK_FAILED, TASK_REJECTED, TASK_INPROGRESS])

        # Check the log output for the success message
        success_message = "Received Store Response (Status: 0x0000 - Success)"
        log_output = "\n".join(log.output)
        self.assertIn(success_message, log_output)



if __name__ == "__main__":
    unittest.main()