from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app, Flask
from .backend_scripts.XSS import xss_testing
from .backend_scripts.SQL_Injection import sql_injection
from datetime import datetime
from webapp.models import XSSResult
from webapp.models import SQLResult
from pymongo import MongoClient
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, session
import os
import threading
import uuid

test_routes = Blueprint("test_routes", __name__)

# Global dictionary to track test statuses
test_status = {}
status_lock = threading.Lock()  # Lock for thread-safe updates

def run_security_tests(url, task_id):
    """Function to run security tests and update test status safely."""
    with status_lock:
        test_status[task_id] = {"status": "running"}

    try:
        # Run security tests
        xss_results = xss_testing(url)
        sql_results = sql_injection(url, 1, 1)

        # Convert datetime to ISO string for compatibility with MongoDB
        xss_results['timestamp'] = xss_results['timestamp'].isoformat()
        sql_results['timestamp'] = sql_results['timestamp'].isoformat()


        # Check if the results are empty or invalid
        if not xss_results or not sql_results:
            raise ValueError("XSS or SQL Injection results are empty or invalid.")

        db = current_app.db
        if db:
            db.xss_result.store_xssresult(xss_results)
            db.sql_result.store_sqlresult(sql_results)

        else:
            raise Exception("Database connection is missing")

        with status_lock:
            test_status[task_id] = {"status": "completed"}

    except Exception as e:
        with status_lock:
            test_status[task_id] = {"status": "failed", "error": str(e)}

@test_routes.route("/run_tests", methods=["POST"])
def run_tests():
    try:
        url = request.json.get("url")  # ✅ Ensure JSON request parsing
        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        task_id = str(uuid.uuid4())  # ✅ Generate a unique task ID

        # Start the test in a separate thread
        thread = threading.Thread(target=run_security_tests, args=(url, task_id))
        thread.start()

        # ✅ Return JSON response with task_id
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
    return jsonify(status)

@test_routes.route("/test_results")
def test_results():
    """Retrieve and display the most recent test results."""
    db = current_app.db
    if not db:
        return jsonify({"error": "Database connection is missing"}), 500

    xss_result = db.xss_result.find_one(sort=[("timestamp", -1)]) or {}
    sql_result = db.sql_result.find_one(sort=[("timestamp", -1)]) or {}

    num_tests = (xss_result.get("num_passed", 0) + xss_result.get("num_failed", 0) +
                 sql_result.get("num_passed", 0) + sql_result.get("num_failed", 0))
    num_failed = xss_result.get("num_failed", 0) + sql_result.get("num_failed", 0)

    return render_template("test_results.html", num_tests=num_tests, num_failed=num_failed)
