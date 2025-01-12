from fastapi import FastAPI, HTTPException, Request
from fhir.resources.bundle import Bundle
from fhir.resources.task import Task
from fhir.resources.operationoutcome import OperationOutcome

from fhir2dicom4ortho.scheduler import scheduler
from fhir2dicom4ortho.tasks import process_bundle, TASK_RECEIVED
from fhir2dicom4ortho.task_store import TaskStore
from fhir2dicom4ortho import logger

fhir_api_app = FastAPI()

# In-memory task store
task_store = TaskStore()

@fhir_api_app.post("/fhir/Bundle")
async def handle_bundle(request: Request):
    try:
        bundle_data = await request.json()
        bundle = Bundle(**bundle_data)
        for entry in bundle.entry:
            if not entry.resource:
                raise HTTPException(status_code=400, detail="Invalid Bundle: Entry must contain a resource")
            resource = entry.resource
            if isinstance(resource, Task):
                task:Task = resource
                break

        # Update Task status resource to represent the job
        task.status = TASK_RECEIVED
        task.description = "Processing Bundle"
        task = task_store.add_task(task)
        # Schedule the job with APScheduler
        job = scheduler.add_job(process_bundle, args=[bundle, task.id, task_store])
        logger.info(f"Job scheduled: {job.id}")

        task_store.modify_task_status(task.id, TASK_RECEIVED)
        return task.model_dump()

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@fhir_api_app.get("/fhir/Task/{task_id}")
async def get_task_status(task_id: str):
    try:
        task = task_store.get_fhir_task_by_id(task_id)
        if not task:
            operation_outcome = OperationOutcome(
                issue=[{
                    "severity": "error",
                    "code": "not-found",
                    "diagnostics": f"Task with ID {task_id} not found"
                }]
            )
            return operation_outcome.model_dump(), 404

        return task.model_dump()


    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")