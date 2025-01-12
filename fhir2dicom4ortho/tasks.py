from dicom4ortho.controller import OrthodonticController
from fhir2dicom4ortho.utils import convert_binary_to_image, convert_binary_to_dataset
from fhir.resources.bundle import Bundle
from fhir.resources.binary import Binary
from fhir.resources.task import Task
from fhir2dicom4ortho import logger, args_cache

TASK_DRAFT = "draft"
TASK_RECEIVED = "received"
TASK_COMPLETED = "completed"
TASK_REJECTED = "rejected"
TASK_FAILED = "failed"
TASK_INPROGRESS = "in-progress"

def process_bundle(bundle:Bundle, task_id, task_store):
    logger.info(f"Processing Task: {task_id}")
    task_store.modify_task_status(task_id, TASK_INPROGRESS)
    try:
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
            task_store.modify_task_status(task_id, TASK_REJECTED)
            raise ValueError("Invalid Bundle: Must contain one image Binary and one DICOM Binary")

        # Convert Binary resources to image and dataset
        image = convert_binary_to_image(image_binary)
        dataset = convert_binary_to_dataset(dicom_binary)

        # Initialize the OrthodonticController
        controller = OrthodonticController()

        # Convert image and dataset to an orthodontic photograph
        orthodontic_photograph = controller.convert_image_plus_mwl_to_dicom4orthograph(image, dataset)
        controller.send(
            send_method=args_cache.pacs_send_method,
            pacs_dimse_hostname=args_cache.pacs_dimse_hostname,
            pacs_dimse_port=args_cache.pacs_dimse_port,
            pacs_dimse_aet=args_cache.pacs_dimse_aet,
            pacs_wado_url=args_cache.pacs_wado_url,
            pacs_wado_username=args_cache.pacs_wado_username,
            pacs_wado_password=args_cache.pacs_wado_password,
            orthodontic_series=orthodontic_photograph.series,
            dicom_datasets=[orthodontic_photograph.to_dataset()]
        )

        # Update task status to completed
        task_store.modify_task_status(task_id, TASK_COMPLETED)
        logger.info(f"Task {task_id} completed")

        # Log the resources
        logger.debug(image_binary.model_dump_json(indent=2))
        logger.debug(dicom_binary.model_dump_json(indent=2))

    except Exception as e:
        task_store.modify_task_status(task_id, TASK_FAILED)
        logger.exception(e)
        logger.error(f"Error processing Bundle: {e}")