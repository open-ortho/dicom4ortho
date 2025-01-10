from fastapi import FastAPI, HTTPException, Request
from fhir.resources.bundle import Bundle
from fhir.resources.task import Task
from fhir2dicom4ortho.scheduler import scheduler
from fhir2dicom4ortho.tasks import process_bundle, TASK_RECEIVED
import uuid

fhir_api_app = FastAPI()

# In-memory task store
task_store = {}

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
        task_store[task.id] = task

        # Schedule the job with APScheduler
        scheduler.add_job(process_bundle, args=[bundle_data, task.id, task_store])

        return task.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@fhir_api_app.get("/fhir/Task/{task_id}")
async def get_task_status(task_id: str):
    task:Task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()