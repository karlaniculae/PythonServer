from app import webserver
from flask import request, jsonify

from app.data_ingestor import DataIngestor
from app.job_work import Job
from app.singletone_pattern.singletone_queues import QueueSingleton
from app.task_runner import ThreadPool
from app.queues import JobManager
import os
import json

job_manager = JobManager()
flag_status = False


# Example endpoint definition
@webserver.route("/api/post_endpoint", methods=["POST"])
def post_endpoint():
    """post_end"""
    if request.method == "POST":
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")
        webserver.logger.info("Post endpoint %s", data)
        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}
        return jsonify(response)
        webserver.logger.error("Method not allowed")
        return jsonify({"error": "Method not allowed"}), 405


@webserver.route("/api/get_results/<job_id>", methods=["GET"])
def get_response(job_id):
    """get_res"""

    print(f"JobID is {job_id}")

    webserver.logger.info("get_response %s", job_id)

    
    if not os.path.exists('results'):
        os.mkdir('results')
    cale_fisier_final = f"./results/{job_id}.json"
    cale_fisier_temporar = f"./results/{job_id}.temp"

    if os.path.exists(cale_fisier_final):
        with open(cale_fisier_final, "r") as file:
            result_data = json.load(file)
            webserver.logger.info("get_results for job_id=%s status=done", job_id)
            return jsonify({"status": "done", "data": result_data})
    elif os.path.exists(cale_fisier_temporar):
        webserver.logger.info("get_results for job_id=%s status=running", job_id)
        return jsonify({"status": "running"})
    else:
        webserver.logger.error("Get_results for job_id=%s status=failed", job_id)
        return jsonify({"error": "Invalid job_id"}), 404


@webserver.route("/api/jobs", methods=["GET"])
def get_jobs_state():
    """jobs"""
    job_statuses = []
    webserver.logger.info("Get_jobs_state")
    for filename in os.listdir("./results/"):
        if filename.endswith(".temp"):
            job_id = filename.replace(".temp", "")
            status = "running"
        elif filename.endswith(".json"):
            job_id = filename.replace(".json", "")
            status = "done"
    job_statuses.append({f"{job_id}": status})
    webserver.logger.info("get_status %s", job_statuses)
    return jsonify({"status": "done", "data": job_statuses})


@webserver.route("/api/graceful_shutdown", methods=["GET"])
def get_graceful_shutdown():
    """graceful_shutdown"""
    #create a flag to stop the threads
    webserver.tasks_runner.flag_status = True
    webserver.logger.info("graceful_shutdown")
    #notify
    webserver.tasks_runner.shutdown()
    return jsonify({"message": "Shutdown started now"}), 200


@webserver.route("/api/num_jobs", methods=["GET"])
def num_jobs():
    """num_jobs"""
    num_jobs = 0
    #count the number of jobs
    for filename in os.listdir("./results/"):
        if filename.endswith(".temp"):
            num_jobs += 1
    webserver.logger.info("the number of jobs is %s", num_jobs)
    return jsonify({"num_jobs": num_jobs})


@webserver.route("/api/states_mean", methods=["POST"])
def states_mean_request():
    """states_mean"""
    
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    #add logg
    webserver.logger.info("Stats_mean question=%s", y)
    job_id = f"job_id_{webserver.job_counter }"
    type_of_question = "states_mean"
    if webserver.tasks_runner.flag_status is False:
        webserver.job_counter += 1
        webserver.logger.info("States_mean status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in states_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/state_mean", methods=["POST"])
def state_mean_request():
    """state_mean"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    state = data["state"]
    webserver.logger.info("State_mean question=%s name of the state %s", y, state)
    type_of_question = "state_mean"
    job_id = f"job_id_{webserver.job_counter}"
    if webserver.tasks_runner.flag_status is False:
        webserver.job_counter += 1
        job_manager.add_job(webserver.job_counter - 1, y, type_of_question, state)
        with webserver.tasks_runner.condition:
            webserver.logger.info("State_mean status=success job_id=%s", job_id)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in state_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/best5", methods=["POST"])
def best5_request():
    """best5"""

    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    webserver.logger.info("Best5 question=%s", y)
    type_of_question = "best5"
    job_id = f"job_id_{webserver.job_counter}"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1 #increment the job counter
        webserver.logger.info("Best5 status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in best5_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/worst5", methods=["POST"])
def worst5_request():
    """worst5"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    webserver.logger.info("Worst5 question=%s", y)
    type_of_question = "worst5"
    job_id = f"job_id_{webserver.job_counter }"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("Worst5 status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in worst5_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/global_mean", methods=["POST"])
def global_mean_request():
    """global_mean"""

    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    webserver.logger.info("Global_mean question=%s", y)
    type_of_question = "global_mean"
    job_id = f"job_id_{webserver.job_counter}"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("Global_mean status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in global_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/diff_from_mean", methods=["POST"])
def diff_from_mean_request():
    """diff_from_mean"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    webserver.logger.info("Diff_from_mean question=%s", y)
    type_of_question = "diff_from_mean"
    job_id = f"job_id_{webserver.job_counter}"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("Diff_from_mean status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in diff_from_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/state_diff_from_mean", methods=["POST"])
def state_diff_from_mean_request():
    """state_diff_fm"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    state = data["state"]
    webserver.logger.info(
        "State_diff_from_mean question=%s name of the state %s", y, state
    )
    type_of_question = "state_diff_from_mean"
    job_id = f"job_id_{webserver.job_counter }"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("State_diff_from_mean status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, state)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in state_diff_from_mean_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/mean_by_category", methods=["POST"])
def mean_by_category_request():
    """mean_bg"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    webserver.logger.info("Mean_by_category question=%s", y)
    type_of_question = "mean_by_category"
    job_id = f"job_id_{webserver.job_counter }"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("Mean_by_category status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, None)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})
    webserver.logger.error("Error in mean_by_category_request")
    return jsonify({"status": "failed", "job_id": job_id})


@webserver.route("/api/state_mean_by_category", methods=["POST"])
def state_mean_by_category_request():
    """state_mean_bgr"""
    data = request.json
    print(f"Got request {data}")
    y = data["question"]
    state = data["state"]
    webserver.logger.info(
        "State_mean_by_category question=%s name of the state %s", y, state
    )
    type_of_question = "state_mean_by_category"
    job_id = f"job_id_{webserver.job_counter }"
    if not webserver.tasks_runner.shutdown_event.is_set():
        webserver.job_counter += 1
        webserver.logger.info("State_mean_by_category status=success job_id=%s", job_id)
        with webserver.tasks_runner.condition:
            job_manager.add_job(webserver.job_counter - 1, y, type_of_question, state)
            webserver.tasks_runner.condition.notify_all()
        return jsonify({"status": "success", "job_id": job_id})


# You can check localhost in your browser to see what this displays
@webserver.route("/")
@webserver.route("/index")
def index():
    """index"""
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg


def get_defined_routes():
    """Get_defined_routes"""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ", ".join(rule.methods)
        routes.append(f'Endpoint: "{rule}" Methods: "{methods}"')
    return routes
