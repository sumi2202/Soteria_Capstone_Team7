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


def check_verified_links(user_email, app):
    """ Continuously checks for verified URLs that need notifications and updates their status. """
    with app.app_context():
        db = current_app.db  # Ensure we are in app context
        print(f"🔍 Checking verified links for {user_email}...")  # Debug message

        while True:
            users = db.registered_urls.distinct("email", {"verified": True, "notified": False})

            for email in users:
                # Find URLs that are verified but not notified for the given user
                urls_to_notify = db.registered_urls.find({
                    "email": email,
                    "verified": True,
                    "notified": False
                })

                for url_doc in urls_to_notify:
                    user_id = url_doc.get("user_id")
                    url = url_doc.get("url")

                    if not user_id:
                        continue

                    # Create the notification
                    timestamp = datetime.now(timezone.utc)
                    notification = {
                        "user_id": str(user_id),
                        "message": f"✅ Your link {url} has been verified!",
                        "timestamp": timestamp,
                        "type": "link_verified"
                    }

                    db.notifications.insert_one(notification)

                    # Mark the URL as notified to avoid duplicate notifications
                    db.registered_urls.update_one(
                        {"_id": url_doc["_id"]},
                        {"$set": {"notified": True}}
                    )

                    print(f"[INFO] 🔔 Notification sent for {url}")

            # Wait before checking again
            time.sleep(30)  # Runs every 30 seconds


@test_routes.route('/start_checking_verified_links')
def start_checking_verified_links():
    """ Starts the background process if not already running. """
    global notification_thread  # Keep track of the thread globally

    if not session.get('email'):
        return "User not logged in or session expired", 400

    if "notification_thread" not in globals() or not notification_thread.is_alive():
        app = current_app._get_current_object()
        notification_thread = threading.Thread(target=check_verified_links, args=(app,), daemon=True)
        notification_thread.start()
        print("[INFO] ✅ Background notification thread started.")

    return "Background notification thread is running."