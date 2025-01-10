from fastapi import FastAPI, HTTPException, Request
from fhir.resources.bundle import Bundle
from fhir.resources.task import Task
from fhir2dicom4ortho.scheduler import scheduler
from fhir2dicom4ortho.tasks import process_bundle
import uuid

fhir_api_app = FastAPI()

# In-memory job store (for demonstration purposes)
job_store = {}

@fhir_api_app.post("/fhir/Bundle")
async def handle_bundle(request: Request):
    try:
        bundle_data = await request.json()

        # Create a new Task resource to represent the job
        job_id = str(uuid.uuid4())
        task = Task(
            id=job_id,
            status="in-progress",
            intent="order",
            description="Processing Bundle"
        )
        job_store[job_id] = {"task": task, "status": "in-progress"}

        # Schedule the job with APScheduler
        scheduler.add_job(process_bundle, args=[bundle_data, job_id, job_store])

        return {"task_id": job_id, "status": task.status}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@fhir_api_app.get("/fhir/Task/{task_id}")
async def get_task_status(task_id: str):
    job = job_store.get(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": job["status"]}