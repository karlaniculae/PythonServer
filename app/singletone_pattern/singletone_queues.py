"""Create a single instance"""
from queue import Queue
from threading import Condition, Event

class QueueSingleton:
    """The class for the single instance"""
    _instance = None
    queue1 = None
    condition = None
    shutdown_event = None

    def __new__(cls):
        """The method for the sngle instance"""
        if cls._instance is None:
            cls._instance = super(QueueSingleton, cls).__new__(cls)
            cls.queue1 = Queue()
            cls.condition = Condition()
            cls.shutdown_event = Event()
        return cls._instance
    