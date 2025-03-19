import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from .backend_scripts.XSS import xss_testing
from .backend_scripts.SQL_Injection import sql_injection
import threading
import uuid

test_routes = Blueprint("test_routes", __name__)

# Global dictionary to track test statuses
test_status = {}
status_lock = threading.Lock()  # Lock for thread-safe updates

def run_security_tests(url, task_id, db):
    """Function to run security tests and update test status safely."""
    with status_lock:
        test_status[task_id] = {"status": "running"}

    try:
        # Run security tests
        xss_results = xss_testing(url)
        sql_results = sql_injection(url, 1, 1)

        # Convert datetime to ISO format for MongoDB
        xss_results['timestamp'] = xss_results['timestamp'].isoformat()
        sql_results['timestamp'] = sql_results['timestamp'].isoformat()

        # Ensure task_id is included in the results for tracking
        xss_results['task_id'] = task_id
        sql_results['task_id'] = task_id

        # Insert into the database within the app context
        db.xss_result.insert_one(xss_results)
        db.sql_result.insert_one(sql_results)

        # Use the app context here explicitly
        with current_app.app_context():
            # Generate the redirect URL using app context (url_for)
            redirect_url = url_for("test_routes.test_results", task_id=task_id)

        with status_lock:
            test_status[task_id] = {"status": "completed", "redirect": redirect_url}

    except Exception as e:
        with status_lock:
            test_status[task_id] = {"status": "failed", "error": str(e)}

@test_routes.route("/run_tests", methods=["POST"])
def run_tests():
    try:
        url = request.json.get("url")
        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        task_id = str(uuid.uuid4())

        db = current_app.db  # Get DB from Flask app

        thread = threading.Thread(target=run_security_tests, args=(url, task_id, db))
        thread.start()

        return jsonify({"success": True, "task_id": task_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@test_routes.route("/loading")
def loading_screen():
    """Render the loading screen while tests are running."""
    task_id = request.args.get("task_id")  # Get task_id from URL
    if not task_id:
        return "Missing task_id", 400  # Handle missing task ID

    return render_template("loading_screen.html", task_id=task_id)

@test_routes.route("/test_status/<task_id>")
def test_status_check(task_id):
    """Check the status of a running or completed security test."""
    with status_lock:
        status = test_status.get(task_id, {"status": "unknown"})

    if status['status'] == 'completed':
        return jsonify({'status': 'completed', 'redirect': url_for("test_routes.test_results", task_id=task_id)})
    else:
        return jsonify({'status': 'running'})

@test_routes.route("/test_results/<task_id>")
def test_results(task_id):
    """Retrieve and display the test results for a given task_id."""
    db = current_app.db

    # Get the test results for the provided task_id
    xss_result = db.xss_result.find_one({"task_id": task_id}) or {}
    sql_result = db.sql_result.find_one({"task_id": task_id}) or {}

    # If no results, return an error
    if not xss_result and not sql_result:
        return jsonify({"error": "No results found for this test"}), 404

    # Calculate the number of tests and failures
    num_tests = (xss_result.get("num_passed", 0) + xss_result.get("num_failed", 0) +
                 sql_result.get("num_passed", 0) + sql_result.get("num_failed", 0))
    num_failed = xss_result.get("num_failed", 0) + sql_result.get("num_failed", 0)

    # Pass data to the template
    return render_template("test_results.html",
                           num_tests=num_tests,
                           num_failed=num_failed,
                           xss_result=xss_result,
                           sql_result=sql_result)

