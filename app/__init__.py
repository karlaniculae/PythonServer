"""init file for the app module"""
import logging
from logging.handlers import RotatingFileHandler
import time
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
import os

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()
webserver.tasks_runner.start_workers()
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")



webserver.job_counter = 1
log_filename = 'webserver.log'

if os.path.exists(log_filename):
    os.remove(log_filename)

webserver.logger = logging.getLogger('webserver_log')

webserver.logger.setLevel(logging.INFO) 


webserver.handler = RotatingFileHandler(log_filename, maxBytes=10000, backupCount=3)
webserver.handler.setLevel(logging.INFO)

formatter = (logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                                datefmt='%Y-%m-%dT%H:%M:%SZ'))
webserver.handler.setFormatter(formatter)
webserver.handler.converter = time.gmtime

webserver.logger.addHandler(webserver.handler)


from app import routes
import signal
