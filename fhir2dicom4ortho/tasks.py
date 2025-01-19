from fhir.resources.bundle import Bundle
from fhir.resources.binary import Binary
from fhir2dicom4ortho import logger, args_cache

from dicom4ortho.controller import OrthodonticController
from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
# from fhir2dicom4ortho.task_store import TaskStore # Cannot import TaskStore for circular import
from fhir2dicom4ortho.utils import get_scheduled_protocol_from_basic, convert_binary_to_dataset, get_opor_code_value_from_code

TASK_DRAFT = "draft"
TASK_RECEIVED = "received"
TASK_COMPLETED = "completed"
TASK_REJECTED = "rejected"
TASK_FAILED = "failed"
TASK_INPROGRESS = "in-progress"

def build_and_send_dicom_image(bundle:Bundle, task_id, task_store):
    """ Build a DICOM image and send it to PACS from a FHIR Bundle containing a Binary image, Binary DICOM MWL, a Basic with code..
    """
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
        scheduled_protocol_code = get_scheduled_protocol_from_basic(mwl_dataset)
        scheduled_protocol_code_value = get_opor_code_value_from_code(scheduled_protocol_code)

        logger.debug("Building OrthodonticPhotograph")
        orthodontic_photograph:OrthodonticPhotograph = OrthodonticPhotograph(
            input_image_bytes=image_binary.data,
            image_type=scheduled_protocol_code_value,
            dicom_mwl=mwl_dataset
        )
        
        logger.debug("Copying MWL tags to OrthodonticPhotograph")
        orthodontic_photograph.copy_mwl_tags(dicom_mwl=mwl_dataset)
        orthodontic_photograph.prepare()


        logger.debug("Sending OrthodonticPhotograph to PACS")
        controller = OrthodonticController()
        result = controller.send(
            send_method=args_cache.pacs_send_method,
            pacs_dimse_hostname=args_cache.pacs_dimse_hostname,
            pacs_dimse_port=args_cache.pacs_dimse_port,
            pacs_dimse_aet=args_cache.pacs_dimse_aet,
            pacs_wado_url=args_cache.pacs_wado_url,
            pacs_wado_username=args_cache.pacs_wado_username,
            pacs_wado_password=args_cache.pacs_wado_password,
            dicom_datasets=[orthodontic_photograph.to_dataset()]
        )

        task_status = get_status_from_response(result)
        logger.debug(f"Setting Task status to {task_status}")
        task_store.modify_task_status(task_id, get_status_from_response(result))
        logger.info(f"Task {task_id} {task_status}")

        # Log the resources
        # logger.debug(image_binary.model_dump_json(indent=2))
        # logger.debug(dicom_binary.model_dump_json(indent=2))

    except Exception as e:
        task_store.modify_task_status(task_id, TASK_FAILED)
        logger.exception(e)
        logger.error(f"Error processing Bundle: {e}")

def get_status_from_response(response):
    """ Set the status of a task from a response object
    """
    if response is None:
        return TASK_FAILED

    # DICOM DIMSE response
    if "Status" in response:
        if response.Status == 0x0000:
            return TASK_COMPLETED

    # DICOM WADO response
    if "status_code" in response:
        if response.status_code == 200:
            return TASK_COMPLETED
    if response.status_code == 200:
        return TASK_COMPLETED
    
    return TASK_FAILED