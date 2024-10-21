"""Instance of a job"""
class Job:
    """The class which has the instance of a job"""
    def __init__(self, job_id, request_question,type_of_question, state = None):
        self.job_id = job_id
        self.request_question = request_question
        self.type_of_question = type_of_question
        self.state = state