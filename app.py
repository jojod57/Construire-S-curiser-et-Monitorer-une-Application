from flask import Flask, request, jsonify, abort
from prometheus_flask_exporter import PrometheusMetrics

"""
Simple TODO API built with Flask.

This application exposes a few REST endpoints to manage a list of tasks in memory.
Each task has an ``id``, a ``title``, an optional ``description`` and a boolean
flag ``done``.  The API allows clients to list existing tasks, create new tasks,
mark a task as completed and delete tasks.  It is deliberately kept simple and
stateless: tasks are stored in a Python list that resets each time the
application restarts.  In a production system you would persist data to a
database or external store, but for the purposes of this exercise an
in-memory store keeps the focus on the CI/CD and security aspects.

Metrics are automatically exported via the ``/metrics`` endpoint thanks to
the ``prometheus_flask_exporter`` library.  This allows Prometheus to scrape
standard HTTP request metrics such as request durations and counts.  See
``requirements.txt`` for all dependencies.

To run the application locally:

.. code:: bash

   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py

The server will listen on ``http://0.0.0.0:5000`` by default.  When running
inside Docker, the exposed port can be mapped to a host port (see
``Dockerfile`` and ``docker-compose.yml``).
"""

app = Flask(__name__)
# PrometheusMetrics binds to the default /metrics endpoint and collects
# request latencies, counts, and common HTTP metrics automatically.
metrics = PrometheusMetrics(app)

# In-memory list of tasks.  Each task is represented as a dictionary.
tasks = []
next_id = 1


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint.

    Returns a simple message confirming that the API is running.  This route
    does not interact with the task list and can be used by external
    monitoring systems to verify that the service is reachable.
    """
    return "OK"


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Return all current tasks.

    Returns a JSON array of task objects.  The list reflects the current
    in‑memory state of the application.  If no tasks have been created yet,
    the returned array will be empty.
    """
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task.

    Expects JSON data with a ``title`` field and optionally a ``description``.
    If the JSON body is missing or ``title`` is not present, the request
    returns a 400 Bad Request.  Successful creation increments the global
    task identifier and appends the new task to the list.
    """
    global next_id
    if not request.is_json:
        abort(400, description="Expected JSON body")
    data = request.get_json()
    title = data.get("title")
    if not title:
        abort(400, description="Missing 'title' field")
    description = data.get("description", "")
    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "done": False,
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def mark_task_done(task_id: int):
    """Mark an existing task as completed.

    Looks up the task by ID and sets its ``done`` flag to ``True``.  If the
    task cannot be found, a 404 Not Found response is returned.  The updated
    task is returned as JSON on success.
    """
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return jsonify(task)
    abort(404, description="Task not found")


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    """Delete a task by ID.

    Removes a task from the list.  Returns a 204 No Content response if the
    deletion succeeds.  Returns 404 if the task does not exist.
    """
    global tasks
    for task in tasks:
        if task["id"] == task_id:
            tasks = [t for t in tasks if t["id"] != task_id]
            return "", 204
    abort(404, description="Task not found")


@app.route("/error", methods=["GET"])
def trigger_error():
    """Endpoint that triggers an intentional error to test incident handling.

    The division by zero below will raise a ZeroDivisionError and result in
    a 500 Internal Server Error response.  Students can hit this route
    deliberately (e.g. GET /error) to simulate an application failure and
    observe the impact on their monitoring stack.
    """
    return 1 / 0  # ZeroDivisionError


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring systems.
    
    Returns a simple "OK" message to indicate the service is running.
    This endpoint can be used by load balancers, monitoring systems,
    or Kubernetes health checks.
    """
    return "OK"


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=False)


