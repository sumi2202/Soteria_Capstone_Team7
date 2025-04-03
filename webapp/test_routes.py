import time
import os
import threading
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import (
    Blueprint, request, jsonify, render_template, redirect,
    url_for, current_app, send_file, session
)
from flask_login import current_user
from .backend_scripts.pdf_generator import pdf_converter
from .backend_scripts.XSS import xss_testing
from .backend_scripts.SQL_Injection import sql_injection
from webapp import socketio

test_routes = Blueprint("test_routes", __name__)

def run_security_tests(app, url, task_id, level, risk, user_id, label):
    with app.app_context():
        db = app.db

        def update_progress(percent):
            db.test_status.update_one(
                {"task_id": task_id},
                {"$set": {"progress": percent}},
                upsert=True
            )

        try:
            db.test_status.insert_one({
                "task_id": task_id,
                "status": "running",
                "progress": 0
            })

            print(f"[START] Running tests for {task_id} with user_id: {user_id}")

            update_progress(10)
            xss_results = xss_testing(url, progress_callback=update_progress)
            update_progress(55)
            sql_results = sql_injection(url, level, risk, progress_callback=update_progress)
            update_progress(95)

            timestamp = datetime.now(timezone.utc)

            xss_results.update({
                "timestamp": timestamp,
                "task_id": task_id,
                "user_id": str(user_id)
            })
            sql_results.update({
                "timestamp": timestamp,
                "task_id": task_id,
                "user_id": str(user_id),
                "level": level,
                "risk": risk,
                "label": label
            })

            db.xss_result.insert_one(xss_results)
            db.sql_result.insert_one(sql_results)

            toronto_time = timestamp.astimezone(ZoneInfo("America/Toronto"))
            formatted_time = toronto_time.strftime('%Y-%m-%d %I:%M %p %Z')

            notification = {
                "user_id": str(user_id),
                "message": f"🧪 Test completed for {url}",
                "timestamp": timestamp,
                "task_id": task_id,
                "type": "test_result"
            }

            db.notifications.insert_one(notification)
            print(f"[MONGO] ✅ Notification inserted: {notification}")

            socketio.emit("new_notification", {
                "message": notification["message"],
                "timestamp": formatted_time
            })

            db.test_status.update_one(
                {"task_id": task_id},
                {"$set": {
                    "status": "completed",
                    "progress": 100,
                    "redirect": f"/tests/test_results/{task_id}"
                }}
            )

        except Exception as e:
            db.test_status.update_one(
                {"task_id": task_id},
                {"$set": {
                    "status": "failed",
                    "progress": 100,
                    "error": str(e)
                }}
            )
            print(f"[ERROR] Test for {task_id} failed: {e}")

@test_routes.route("/run_tests", methods=["POST"])
def run_tests():
    data = request.json if request.is_json else request.form
    url = data.get("url")
    level_risk = data.get("sql_level_risk", "1,1").split(",")
    level, risk = int(level_risk[0]), int(level_risk[1])
    label = data.get("sql_label", "Unknown Testing Level")
    task_id = str(uuid.uuid4())
    user_id = session.get("user_id")

    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400
    if not user_id:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    app = current_app._get_current_object()
    thread = threading.Thread(target=run_security_tests, args=(app, url, task_id, level, risk, user_id, label))
    thread.start()

    return jsonify({
        "success": True,
        "task_id": task_id,
        "redirect": url_for("test_routes.loading_screen", task_id=task_id)
    })

@test_routes.route("/loading")
def loading_screen():
    task_id = request.args.get("task_id")
    if not task_id:
        return "Missing task_id", 400
    return render_template("loading_screen.html", task_id=task_id)

@test_routes.route("/test_status/<task_id>")
def test_status_check(task_id):
    db = current_app.db
    status = db.test_status.find_one({"task_id": task_id}) or {"status": "unknown", "progress": 0}
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

    raw_ts = xss_result.get("timestamp")
    formatted_ts = "---"
    try:
        if isinstance(raw_ts, str):
            if raw_ts.endswith("Z"):
                raw_ts = raw_ts.replace("Z", "+00:00")
            raw_ts = datetime.fromisoformat(raw_ts)

        if isinstance(raw_ts, datetime):
            if raw_ts.tzinfo is None:
                raw_ts = raw_ts.replace(tzinfo=timezone.utc)
            raw_ts = raw_ts.astimezone(ZoneInfo("America/Toronto"))

        formatted_ts = raw_ts.strftime("%Y-%m-%d %I:%M %p %Z")
    except Exception as e:
        print(f"[ERROR] Failed to format timestamp for task {task_id}: {e}")

    return render_template("test_results.html",
                           num_tests=num_tests,
                           num_failed=num_failed,
                           xss_result=xss_result,
                           sql_result=sql_result,
                           formatted_timestamp=formatted_ts)

@test_routes.route("/download/<task_id>")
def download_pdf(task_id):
    db = current_app.db
    xss_result = db.xss_result.find_one({"task_id": task_id})

    if not xss_result:
        return "No test data found", 404

    url = xss_result.get("url") or "---"
    pdf_path = pdf_converter(url, task_id)

    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return "PDF not found", 404

@test_routes.route("/notifications", methods=["GET"])
def get_user_notifications():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    db = current_app.db
    results = db.notifications.find({"user_id": str(user_id)}).sort("timestamp", -1).limit(10)

    notifications = []
    for notif in results:
        toronto_ts = notif["timestamp"].astimezone(ZoneInfo("America/Toronto"))
        notifications.append({
            "message": notif["message"],
            "timestamp": toronto_ts.strftime('%Y-%m-%d %I:%M %p %Z')
        })

    return jsonify({"success": True, "notifications": notifications})

@test_routes.route("/debug-insert")
def debug_insert_notification():
    db = current_app.db
    user_id = session.get("user_id") or "test_user_id"
    timestamp = datetime.utcnow()

    notification = {
        "user_id": str(user_id),
        "message": "🐛 Manual debug insert",
        "timestamp": timestamp,
        "task_id": "debug-task-id",
        "type": "debug"
    }

    try:
        result = db.notifications.insert_one(notification)
        print(f"[DEBUG] Notification manually inserted with ID: {result.inserted_id}")
        return jsonify({"success": True, "notif_id": str(result.inserted_id)})
    except Exception as e:
        print(f"[DEBUG] Manual insert failed: {e}")
        return jsonify({"success": False, "error": str(e)})
