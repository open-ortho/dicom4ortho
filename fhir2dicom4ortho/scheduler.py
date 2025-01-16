# filepath: /home/afm/src/open-ortho/dicom4ortho/fhir2dicom4ortho/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

executors = {
    'default': ThreadPoolExecutor(10)
}

scheduler = BackgroundScheduler(executors=executors)
scheduler.start()