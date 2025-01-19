from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fhir.resources.task import Task as FHIRTask
from fhir2dicom4ortho.tasks import TASK_DRAFT
import uuid

Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String)
    fhir_task = Column(Text, nullable=False)


class TaskStore:
    def __init__(self, db_url='sqlite:///tasks.sqlite'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_task(self, fhir_task: FHIRTask):
        """ Add a new task to the store

        This method is used to add a new task to the store. The task is stored in the database with a unique ID, and the same ID is used to overwrite the FHIR Task ID.
        """
        session = self.Session()
        new_id = str(uuid.uuid4())
        fhir_task.id = new_id
        fhir_task.status = TASK_DRAFT
        new_task = Task(
            id=new_id,
            description=fhir_task.description,
            fhir_task=fhir_task.model_dump_json()
        )
        session.add(new_task)
        session.commit()
        session.close()
        return fhir_task

    def reserve_id(self, description=None, intent="unknown") -> str:
        """ Reserve a new task ID.

        This method is used in order to send the correct task ID to the actual running task process, so it can update the status of the task.
        
        Huh? But the Job is being run by APScheduler, not the Task. The Task is just a record in the database. The Job is the one that needs to update the Task status. So, this method should not be needed: just add the Task to the task store first, then schedule the Job with the Task ID returned...

        Maybe this method is necessary in tests?
        """
        session = self.Session()
        fhir_task = FHIRTask.model_construct(
            status=TASK_DRAFT, description=description, intent=intent)
        new_task = Task(description=description,
                        fhir_task=fhir_task.model_dump_json())
        session.add(new_task)
        session.commit()
        reserved_id = new_task.id
        session.close()
        return reserved_id

    def get_task_by_id(self, task_id) -> FHIRTask:
        session = self.Session()
        task = session.query(Task).filter_by(id=task_id).first()
        session.close()
        return task

    def get_fhir_task_by_id(self, task_id) -> FHIRTask:
        task = self.get_task_by_id(task_id)
        if task:
            fhir_task = FHIRTask.model_validate_json(task.fhir_task)
            return fhir_task
        return None

    def modify_task_status(self, task_id, new_status) -> FHIRTask:
        """ Modify the status of a task by ID
        """
        session = self.Session()
        task = self.get_task_by_id(task_id)
        if task:
            fhir_task = FHIRTask.model_validate_json(task.fhir_task)
            fhir_task.status = new_status
            task.fhir_task = fhir_task.model_dump_json()
            session.add(task)
            session.commit()
        session.close()
        return fhir_task if task else None

    # def modify_task(self, task_id, updated_fhir_task: FHIRTask) -> FHIRTask:
    #     session = self.Session()
    #     task = session.query(Task).filter_by(id=task_id).first()
    #     if task:
    #         existing_fhir_task = FHIRTask.model_parse_raw(task.fhir_task)
    #         # Preserve the id and status
    #         updated_fhir_task.id = existing_fhir_task.id
    #         updated_fhir_task.status = existing_fhir_task.status
    #         task.fhir_task = updated_fhir_task.model_dump_json()
    #         session.commit()
    #     session.close()
    #     return updated_fhir_task if task else None
