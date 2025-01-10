from fastapi import FastAPI, HTTPException, Request
from fhir.resources.bundle import Bundle
from fhir.resources.task import Task
from fhir.resources.binary import Binary
from dicom4ortho.controller import OrthodonticController

from fhir2dicom4ortho.utils import convert_binary_to_image, convert_binary_to_dataset
from fhir2dicom4ortho import logger

fhir_api_app = FastAPI()

@fhir_api_app.post("/Bundle")
async def handle_bundle(request: Request):
    try:
        bundle_data = await request.json()
        bundle = Bundle(**bundle_data)

        # Extract Task and Binary resources
        task = None
        image_binary = None
        dicom_binary = None

        for entry in bundle.entry:
            resource = entry.resource
            if isinstance(resource, Task):
                task = resource
            elif isinstance(resource, Binary):
                if resource.contentType.startswith("image/"):
                    image_binary = resource
                elif resource.contentType == "application/dicom":
                    dicom_binary = resource

        if not task or not image_binary or not dicom_binary:
            raise HTTPException(status_code=400, detail="Invalid Bundle: Must contain one Task, one image Binary, and one DICOM Binary")

        # Convert Binary resources to image and dataset
        image = convert_binary_to_image(image_binary)
        dataset = convert_binary_to_dataset(dicom_binary)

        # Initialize the OrthodonticController
        controller = OrthodonticController()

        # Convert image and dataset to an orthodontic photograph
        orthodontic_photograph = controller.convert_image_plus_mwl_to_dicom4orthograph(image, dataset)

        # Log the resources
        logger.debug(task.model_dump_json(indent=2))
        logger.debug(image_binary.model_dump_json(indent=2))
        logger.debug(dicom_binary.model_dump_json(indent=2))

        return {"status": "success", "message": "Bundle processed successfully"}

    except Exception as e:
        logger.error(f"Error processing Bundle: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")