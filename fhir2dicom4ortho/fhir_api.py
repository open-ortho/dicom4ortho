from fastapi import FastAPI, HTTPException, Request
from fhir.resources.bundle import Bundle
from fhir.resources.task import Task
from fhir.resources.binary import Binary
import logging

app = FastAPI()

@app.post("/Bundle")
async def handle_bundle(request: Request):
    try:
        bundle_data = await request.json()
        bundle = Bundle(**bundle_data)

        # Extract Task and Binary resources
        task = None
        binaries = []

        for entry in bundle.entry:
            resource = entry.resource
            if isinstance(resource, Task):
                task = resource
            elif isinstance(resource, Binary):
                binaries.append(resource)

        if not task or len(binaries) != 2:
            raise HTTPException(status_code=400, detail="Invalid Bundle: Must contain one Task and two Binary resources")

        # Implement your logic to handle the Task and Binary resources
        # For example, you can log the resources
        logging.info(task.model_dump_json(indent=2))
        for binary in binaries:
            logging.info(binary.model_dump_json(indent=2))

        return {"status": "success", "message": "Bundle processed successfully"}

    except Exception as e:
        logging.error(f"Error processing Bundle: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")