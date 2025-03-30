import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from .backend_scripts.XSS import xss_testing
from .backend_scripts.SQL_Injection import sql_injection
from datetime import datetime
import threading
import uuid

test_routes = Blueprint("test_routes", __name__)
test_status = {}
status_lock = threading.Lock()

def run_security_tests(app, url, task_id, level, risk):
    with app.app_context():
        with status_lock:
            test_status[task_id] = {"status": "running", "progress": 0}

        def update_progress(percent):
            with status_lock:
                if task_id in test_status:
                    test_status[task_id]["progress"] = percent

        try:
            print(f"Starting tests for {task_id}...")

            update_progress(10)  # initial
            xss_results = xss_testing(url, progress_callback=update_progress)
            update_progress(55)  # halfway through
            sql_results = sql_injection(url, level, risk, progress_callback=update_progress)
            update_progress(95)  # almost done

            xss_results['timestamp'] = datetime.utcnow()
            sql_results['timestamp'] = datetime.utcnow()
            xss_results['task_id'] = task_id
            sql_results['task_id'] = task_id

            db = app.db
            db.xss_result.insert_one(xss_results)
            db.sql_result.insert_one(sql_results)

            redirect_url = f"/tests/test_results/{task_id}"
            with status_lock:
                test_status[task_id] = {
                    "status": "completed",
                    "redirect": redirect_url,
                    "progress": 100
                }

        except Exception as e:
            with status_lock:
                test_status[task_id] = {"status": "failed", "error": str(e), "progress": 100}
            print(f"Test for {task_id} failed: {e}")

@test_routes.route("/run_tests", methods=["POST"])
def run_tests():
    data = request.json if request.is_json else request.form
    url = data.get("url")
    level_risk = data.get("sql_level_risk", "1,1").split(",")
    level, risk = int(level_risk[0]), int(level_risk[1])
    print(f"Received SQLi Level: {level}, Risk: {risk}")

    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    task_id = str(uuid.uuid4())
    app = current_app._get_current_object()
    thread = threading.Thread(target=run_security_tests, args=(app, url, task_id, level, risk))
    thread.start()

    return jsonify({"success": True, "task_id": task_id, "redirect": url_for("test_routes.loading_screen", task_id=task_id)})


@test_routes.route("/loading")
def loading_screen():
    task_id = request.args.get("task_id")
    if not task_id:
        return "Missing task_id", 400
    return render_template("loading_screen.html", task_id=task_id)

@test_routes.route("/test_status/<task_id>")
def test_status_check(task_id):
    with status_lock:
        status = test_status.get(task_id, {"status": "unknown", "progress": 0})
    return jsonify({
        "status": status.get("status", "unknown"),
        "progress": status.get("progress", 0),
        "redirect": status.get("redirect", "")
    })

@test_routes.route("/test_results/<task_id>")
def test_results(task_id):
    db = current_app.db
    for _ in range(5):
        xss_result = db.xss_result.find_one({"task_id": task_id}) or {}
        sql_result = db.sql_result.find_one({"task_id": task_id}) or {}
        if xss_result or sql_result:
            break
        time.sleep(1)

    if not xss_result and not sql_result:
        return jsonify({"error": "No results found for this test"}), 404

    num_tests = (xss_result.get("num_passed", 0) + xss_result.get("num_failed", 0) +
                 sql_result.get("num_passed", 0) + sql_result.get("num_failed", 0))
    num_failed = xss_result.get("num_failed", 0) + sql_result.get("num_failed", 0)

    return render_template("test_results.html",
                           num_tests=num_tests,
                           num_failed=num_failed,
                           xss_result=xss_result,
                           sql_result=sql_result)
