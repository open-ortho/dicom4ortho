import unittest
from fastapi.testclient import TestClient
from fhir2dicom4ortho.fhir_api import fhir_api_app

# unknown | proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option
base64_sample_data = "VGhpcyBpcyBhIHNhbXBsZSBkaWNvbSBkYXRhLg=="

test_bundle = {
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:task-example",
      "resource": {
        "resourceType": "Task",
        "intent": "order",
        "id": "task-example",
        "status": "requested",
        "description": "Process DICOM MWL and Image Input",
        "authoredOn": "2024-06-16T14:00:00Z",
        "requester": {
          "reference": "Practitioner/456",
          "display": "Dr. John Doe"
        },
        "for": {
          "reference": "Patient/123",
          "display": "Patient Example"
        },
        "input": [
          {
            "type": {
              "text": "DICOM MWL"
            },
            "valueReference": {
              "reference": "Binary/mwl-dicom"
            }
          },
          {
            "type": {
              "text": "Image File"
            },
            "valueReference": {
              "reference": "Binary/image-jpeg"
            }
          }
        ]
      },
      "request": {
        "method": "POST",
        "url": "Task"
      }
    },
    {
      "fullUrl": "urn:uuid:mwl-dicom",
      "resource": {
        "resourceType": "Binary",
        "id": "mwl-dicom",
        "contentType": "application/dicom",
        "data": base64_sample_data
      },
      "request": {
        "method": "POST",
        "url": "Binary"
      }
    },
    {
      "fullUrl": "urn:uuid:image-jpeg",
      "resource": {
        "resourceType": "Binary",
        "id": "image-jpeg",
        "contentType": "image/jpeg",
        "data": base64_sample_data
      },
      "request": {
        "method": "POST",
        "url": "Binary"
      }
    }
  ]
}

class TestFHIRAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(fhir_api_app)

    def test_handle_bundle(self):
        response = self.client.post("/fhir/Bundle", json=test_bundle)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "message": "Bundle processed successfully"})

if __name__ == "__main__":
    unittest.main()