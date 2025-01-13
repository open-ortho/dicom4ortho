from dicom4ortho.controller import OrthodonticController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
from fhir2dicom4ortho.utils import get_code_from_mwl, convert_binary_to_dataset, get_opor_code_value_from_code
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
        logger.debug("Extracting Binary resources")
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

        logger.debug("Converting Binary resources to image and dataset")
        # image = convert_binary_to_image(image_binary)
        mwl_dataset = convert_binary_to_dataset(dicom_binary)
        
        logger.debug("Getting proper 99OPOR image type code from MWL")
        image_type_code = get_code_from_mwl(mwl_dataset)
        image_type_code_value = get_opor_code_value_from_code(image_type_code)

        logger.debug("Building OrthodonticPhotograph")
        orthodontic_photograph:OrthodonticPhotograph = OrthodonticPhotograph(
            input_image_bytes=image_binary.data,
            image_type=image_type_code_value,
            dicom_mwl=mwl_dataset
        )
        
        logger.debug("Copying MWL tags to OrthodonticPhotograph")
        orthodontic_photograph.copy_mwl_tags(dicom_mwl=mwl_dataset)
        orthodontic_photograph.prepare()


        logger.debug("Sending OrthodonticPhotograph to PACS")
        controller = OrthodonticController()
        controller.send(
            send_method=args_cache.pacs_send_method,
            pacs_dimse_hostname=args_cache.pacs_dimse_hostname,
            pacs_dimse_port=args_cache.pacs_dimse_port,
            pacs_dimse_aet=args_cache.pacs_dimse_aet,
            pacs_wado_url=args_cache.pacs_wado_url,
            pacs_wado_username=args_cache.pacs_wado_username,
            pacs_wado_password=args_cache.pacs_wado_password,
            dicom_datasets=[orthodontic_photograph.to_dataset()]
        )

        # Update task status to completed
        logger.debug("Setting Task status to completed")
        task_store.modify_task_status(task_id, TASK_COMPLETED)
        logger.info(f"Task {task_id} completed")

        # Log the resources
        # logger.debug(image_binary.model_dump_json(indent=2))
        # logger.debug(dicom_binary.model_dump_json(indent=2))

    except Exception as e:
        task_store.modify_task_status(task_id, TASK_FAILED)
        logger.exception(e)
        logger.error(f"Error processing Bundle: {e}")