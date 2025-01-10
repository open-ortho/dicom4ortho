from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

executors = {
    'default': ThreadPoolExecutor(10)  # Adjust the number of threads as needed
}

scheduler = BackgroundScheduler(executors=executors)
scheduler.start()