"""Add jobs in the queue"""

from app.singletone_pattern.singletone_queues import QueueSingleton
from app.job_work import Job

class JobManager:
    """The class which has the module to add jobs in the queue"""
    def __init__(self):
        self.job_queue = QueueSingleton().queue1
        self.condition = QueueSingleton().condition
        self.shutdown_event = QueueSingleton().shutdown_event    
    def add_job(self, job_id, request_question, type_of_question,state):
        """Add a new job in the queue"""
        new_job = Job(job_id, request_question, type_of_question, state)
        self.job_queue.put(new_job)