"""Task_runner"""

import json
import logging
import os
from queue import Queue
from threading import Thread

from app.data_ingestor import DataIngestor
from app.singletone_pattern.singletone_queues import QueueSingleton

logging = logging.getLogger("webserver_log")


def states_mean(data_ingestor, request_question):
    """ "states_mean"""
    filtered_data = data_ingestor.data[
        data_ingestor.data["Question"] == request_question
    ]
    state_means = (
        filtered_data.groupby("LocationDesc")["Data_Value"].mean().reset_index()
    )
    sorted_states = state_means.sort_values("Data_Value")
    return sorted_states.set_index("LocationDesc")["Data_Value"].to_dict()


def state_mean(data_ingestor, request_question, state):
    """state_mean"""
    filtered_data = data_ingestor.data[
        (data_ingestor.data["Question"] == request_question)
        & (data_ingestor.data["LocationDesc"] == state)
    ]
    state_mean = filtered_data["Data_Value"].mean()
    return {state: state_mean}


def global_mean(data_ingestor, request_question):
    """global_mean"""
    filtered_data = data_ingestor.data[
        data_ingestor.data["Question"] == request_question
    ]
    global_mean_value = filtered_data["Data_Value"].mean()
    return {"global_mean": global_mean_value}


def diff_from_mean(data_ingestor, request_question, state):
    """diff_from_mean"""
    global_mean_result = global_mean(data_ingestor, request_question)["global_mean"]

    states_data = data_ingestor.data[data_ingestor.data["Question"] == request_question]
    states_mean = states_data.groupby("LocationDesc")["Data_Value"].mean().reset_index()

    states_mean["Diff_From_Global_Mean"] = states_mean["Data_Value"].apply(
        lambda x: global_mean_result - x
    )

    diff_from_mean_dict = dict(
        zip(states_mean["LocationDesc"], states_mean["Diff_From_Global_Mean"])
    )

    return diff_from_mean_dict


def state_diff_from_mean(data_ingestor, request_question, state):
    """state_diff_from_mean"""
    filtered_data_global = data_ingestor.data[
        data_ingestor.data["Question"] == request_question
    ]
    global_mean_value = filtered_data_global["Data_Value"].mean()
    filtered_data_state = data_ingestor.data[
        (data_ingestor.data["Question"] == request_question)
        & (data_ingestor.data["LocationDesc"] == state)
    ]
    state_mean_value = filtered_data_state["Data_Value"].mean()
    diff_from_global_mean = global_mean_value - state_mean_value
    return {state: diff_from_global_mean}


def mean_by_category(data_ingestor, request_question):
    """mean_by_category"""
    filtered_data = data_ingestor.data[
        data_ingestor.data["Question"] == request_question
    ]

    category_means = (
        filtered_data.groupby(
            ["LocationDesc", "StratificationCategory1", "Stratification1"]
        )["Data_Value"]
        .mean()
        .reset_index()
    )
    result_dict = {}

    for index, row in category_means.iterrows():
        state = row["LocationDesc"]
        category = row["StratificationCategory1"]
        segment = row["Stratification1"]
        mean_value = row["Data_Value"]
        key = f"('{state}', '{category}', '{segment}')"

        result_dict[key] = mean_value

    return result_dict


def state_mean_by_category(data_ingestor, request_question, state):
    """state_mean_by_category"""
    filtered_data = data_ingestor.data[
        (data_ingestor.data["Question"] == request_question)
        & (data_ingestor.data["LocationDesc"] == state)
    ]
    category_means = (
        filtered_data.groupby(["StratificationCategory1", "Stratification1"])[
            "Data_Value"
        ]
        .mean()
        .reset_index()
    )

    result_dict = {}
    for index, row in category_means.iterrows():
        category = row["StratificationCategory1"]
        segment = row["Stratification1"]
        value = row["Data_Value"]
        key = f"('{category}', '{segment}')"
        result_dict[key] = value

    return {state: result_dict}


class Calculate:
    """Calculate"""

    def __init__(
        self, job_id, request_question, type_of_question, data_ingestor, state
    ):
        """Calculate"""
        self.job_id = job_id
        self.request_question = request_question
        self.type_of_question = type_of_question
        self.data_ingestor = data_ingestor
        self.state = state

    def process_question(self):
        """process_question"""
        path = "./nutrition_activity_obesity_usa_subset.csv"
        if self.type_of_question == "states_mean":
            logging.info("hello states_mean")
            result = states_mean(self.data_ingestor, self.request_question)
            return result
        if self.type_of_question == "state_mean":
            logging.info("hello state_mean")
            result = state_mean(self.data_ingestor, self.request_question, self.state)
            return result
        if self.type_of_question == "best5":
            logging.info("hello best5")
            filtered_data = self.data_ingestor.data[
                self.data_ingestor.data["Question"] == self.request_question
            ]

            if self.request_question in self.data_ingestor.questions_best_is_min:
                logging.info("hello best5")
                state_means = (
                    filtered_data.groupby("LocationDesc")["Data_Value"]
                    .mean()
                    .reset_index()
                )
                best_states = (
                    state_means.nsmallest(5, "Data_Value")
                    .set_index("LocationDesc")["Data_Value"]
                    .to_dict()
                )
                return best_states

            if self.request_question in self.data_ingestor.questions_best_is_max:
                logging.info("hello best5")
                state_means = (
                    filtered_data.groupby("LocationDesc")["Data_Value"]
                    .mean()
                    .reset_index()
                )
                best_states = (
                    state_means.nlargest(5, "Data_Value")
                    .set_index("LocationDesc")["Data_Value"]
                    .to_dict()
                )
                return best_states

            else:
                return {
                    "error": "Question not found in either best is min or max lists"
                }
        if self.type_of_question == "worst5":
            logging.info("hello worst5")
            filtered_data = self.data_ingestor.data[
                self.data_ingestor.data["Question"] == self.request_question
            ]

            if self.request_question in self.data_ingestor.questions_best_is_min:
                state_means = (
                    filtered_data.groupby("LocationDesc")["Data_Value"]
                    .mean()
                    .reset_index()
                )
                worst_states = (
                    state_means.nlargest(5, "Data_Value")
                    .set_index("LocationDesc")["Data_Value"]
                    .to_dict()
                )
                return worst_states

            if self.request_question in self.data_ingestor.questions_best_is_max:
                state_means = (
                    filtered_data.groupby("LocationDesc")["Data_Value"]
                    .mean()
                    .reset_index()
                )
                worst_states = (
                    state_means.nsmallest(5, "Data_Value")
                    .set_index("LocationDesc")["Data_Value"]
                    .to_dict()
                )
                return worst_states

            else:
                return {
                    "error": "Question not found in either best is min or max lists"
                }
        if self.type_of_question == "global_mean":
            logging.info("hello global_mean")
            result = global_mean(self.data_ingestor, self.request_question)
            logging.info("bye global_mean")
            return result
        if self.type_of_question == "diff_from_mean":
            logging.info("hello diff_from_mean")
            result = diff_from_mean(
                self.data_ingestor, self.request_question, self.state
            )
            logging.info("bye diff_from_mean")
            return result
        if self.type_of_question == "state_diff_from_mean":
            logging.info("hello state_diff_from_mean")
            result = state_diff_from_mean(
                self.data_ingestor, self.request_question, self.state
            )
            logging.info("bye state_diff_from_mean")
            return result
        if self.type_of_question == "mean_by_category":
            logging.info("hello mean_by_category")
            result = mean_by_category(self.data_ingestor, self.request_question)
            logging.info("bye mean_by_category")
            return result
        if self.type_of_question == "state_mean_by_category":
            logging.info("hello state_mean_by_category")
            result = state_mean_by_category(
                self.data_ingestor, self.request_question, self.state
            )
            logging.info("bye state_mean_by_category")
            return result


class ThreadPool:
    """ThreadPool"""

    def __init__(self):
        """ "ThreadPool"""
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        self.flag_status = False
        self.job_queue = QueueSingleton().queue1
        self.condition = QueueSingleton().condition
        self.shutdown_event = QueueSingleton().shutdown_event
        num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count()))
        self.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
        self.workers = [
            TaskRunner(
                self.shutdown_event,
                self.condition,
                self.job_queue,
                self.data_ingestor,
                self.flag_status,
            )
            for _ in range(num_threads)
        ]

    def start_workers(self):
        """start_workers"""
        for worker in self.workers:
            worker.start()

    def shutdown(self):
        """shutdown"""
        with self.condition:
            self.condition.notify_all()


class TaskRunner(Thread):
    """ "TaskRunner"""

    def __init__(
        self, shutdown_event, condition, job_queue, data_ingestor, flag_status
    ):
        super().__init__()
        self.job_queue = job_queue
        self.condition = condition
        self.shutdown_event = shutdown_event
        self.data_ingestor = data_ingestor
        self.flag_status = flag_status
        pass

    def run(self):
        while True:
            while self.flag_status is False:
                with self.condition:
                    self.condition.wait()
                if self.flag_status is True:
                    break
                job = self.job_queue.get()
                if job:
                    if not os.path.exists("results"):
                        os.makedirs("results")

                    result_file_path = f"./results/job_id_{job.job_id}.temp"
                    with open(result_file_path, "w") as temp_file:
                        pass
                    result = Calculate(
                        job.job_id,
                        job.request_question,
                        job.type_of_question,
                        self.data_ingestor,
                        job.state,
                    ).process_question()
                    temp_file_path = f"./results/job_id_{job.job_id}.temp"
                    result_file_path = f"./results/job_id_{job.job_id}.json"
                    with open(temp_file_path, "w") as temp_file:
                        temp_file.write(json.dumps(result))
                    os.rename(temp_file_path, result_file_path)
                    self.job_queue.task_done()
            if not self.job_queue.empty() and self.flag_status is True:
                job = self.job_queue.get()
                if not os.path.exists("results"):
                    os.makedirs("results")
                result_file_path = f"./results/job_id_{job.job_id}.temp"
                with open(result_file_path, "w") as temp_file:
                    pass
                result = Calculate(
                    job.job_id,
                    job.request_question,
                    job.type_of_question,
                    self.data_ingestor,
                    job.state,
                ).process_question()
                temp_file_path = f"./results/job_id_{job.job_id}.temp"
                result_file_path = f"./results/job_id_{job.job_id}.json"
                with open(temp_file_path, "w") as temp_file:
                    temp_file.write(json.dumps(result))
                os.rename(temp_file_path, result_file_path)
