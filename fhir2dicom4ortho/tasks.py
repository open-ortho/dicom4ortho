from dicom4ortho.controller import OrthodonticController
from fhir2dicom4ortho.utils import convert_binary_to_image, convert_binary_to_dataset
from fhir.resources.bundle import Bundle
from fhir.resources.binary import Binary
import logging

def process_bundle(bundle_data, job_id, job_store):
    try:
        bundle = Bundle(**bundle_data)

        # Extract Binary resources
        image_binary = None
        dicom_binary = None

        for entry in bundle.entry:
            resource = entry.resource
            if isinstance(resource, Binary):
                if resource.contentType.startswith("image/"):
                    image_binary = resource
                elif resource.contentType == "application/dicom":
                    dicom_binary = resource

        if not image_binary or not dicom_binary:
            job_store[job_id]["status"] = "failed"
            raise ValueError("Invalid Bundle: Must contain one image Binary and one DICOM Binary")

        # Convert Binary resources to image and dataset
        image = convert_binary_to_image(image_binary)
        dataset = convert_binary_to_dataset(dicom_binary)

        # Initialize the OrthodonticController
        controller = OrthodonticController()

        # Convert image and dataset to an orthodontic photograph
        orthodontic_photograph = controller.convert_image_plus_mwl_to_dicom4orthograph(image, dataset)

        # Update job status to completed
        job_store[job_id]["status"] = "completed"

        # Log the resources
        logging.debug(image_binary.model_dump_json(indent=2))
        logging.debug(dicom_binary.model_dump_json(indent=2))

    except Exception as e:
        logging.error(f"Error processing Bundle: {e}")
        job_store[job_id]["status"] = "failed"