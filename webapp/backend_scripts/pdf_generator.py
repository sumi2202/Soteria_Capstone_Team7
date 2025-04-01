from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "static", "assets"))

LOGO_PATH = os.path.join(STATIC_DIR, "Soteria_logo_white.png")
SOS_EMOJI = os.path.join(STATIC_DIR, "sos.png")
MED_EMOJI = os.path.join(STATIC_DIR, "med.png")
LOW_EMOJI = os.path.join(STATIC_DIR, "low.png")
NO_EMOJI = os.path.join(STATIC_DIR, "no.png")

def safe_text(value):
    try:
        if value is None or str(value).strip().lower() in ["", "none"]:
            return "---"
        return str(value)
    except Exception:
        return "---"

def safe_get(data, key, default="---"):
    try:
        return safe_text(data.get(key, default))
    except Exception:
        return default

def pdf_converter(url, task_id):
    db = current_app.db
    sql_result_data = db.sql_result.find_one({"task_id": task_id})
    xss_result_data = db.xss_result.find_one({"task_id": task_id})

    if not sql_result_data or not xss_result_data:
        return None

    safe_url = safe_text(url)

    pdf_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "pdf_cache"))
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"Soteria_Results_{task_id}.pdf")

    w, h = A4
    file = canvas.Canvas(pdf_path, pagesize=A4)

    def check_space_needed(remaining_space, needed_space):
        if remaining_space < needed_space:
            file.showPage()
            file.drawImage(LOGO_PATH, 40, h - 80, width=65, height=65)
            file.setFont("Times-Roman", 14)
            return h - 130
        return remaining_space

    # Header
    file.drawImage(LOGO_PATH, 40, h - 80, width=65, height=65)
    file.setFont("Times-Bold", 20)
    file.drawString(w / 3, h - 90, "Soteria Testing Overview")

    # URL
    file.setFont("Times-Bold", 13)
    file.drawString(50, h - 130, "URL:")
    file.setFont("Times-Roman", 13)
    file.drawString(85, h - 130, safe_url)

    # Timestamp (force into America/Toronto timezone)
    raw_ts = xss_result_data.get('timestamp')
    try:
        if isinstance(raw_ts, str):
            if raw_ts.endswith("Z"):
                raw_ts = raw_ts.replace("Z", "+00:00")
            raw_ts = datetime.fromisoformat(raw_ts)

        if isinstance(raw_ts, datetime):
            if raw_ts.tzinfo is None:
                raw_ts = raw_ts.replace(tzinfo=timezone.utc)
            raw_ts = raw_ts.astimezone(ZoneInfo("America/Toronto"))

        formatted_time = raw_ts.strftime("%Y-%m-%d %I:%M %p %Z")
    except Exception:
        formatted_time = "---"

    file.setFont("Times-Bold", 13)
    file.drawString(50, h - 150, "Time of Completion:")
    file.setFont("Times-Roman", 13)
    file.drawString(170, h - 150, formatted_time)

    height = h - 180

    def write_test_results(title, data, category):
        nonlocal height
        file.setFont("Times-Bold", 16)
        height = check_space_needed(height, 30)
        file.drawString(50, height, safe_text(title))
        height -= 30

        file.setFont("Times-Roman", 14)
        file.drawString(50, height, f"Passed Tests: {safe_get(data, 'num_passed')}")
        height -= 20
        for i in data.get("type_passed", []):
            height = check_space_needed(height, 15)
            file.drawString(70, height, f"--> {safe_text(i)}")
            height -= 15

        height -= 10
        file.drawString(50, height, f"Failed Tests: {safe_get(data, 'num_failed')}")
        height -= 20
        for j in data.get("type_failed", []):
            height = check_space_needed(height, 15)
            file.drawString(70, height, f"--> {safe_text(j)}")
            height -= 15

        if category == "sql":
            height -= 20
            file.drawString(50, height, "Detected Databases:")
            height -= 20
            for db_item in data.get("database_list", []):
                height = check_space_needed(height, 15)
                file.drawString(70, height, f"--> {safe_text(db_item)}")
                height -= 15

        height -= 20

    write_test_results("SQL Injection Results:", sql_result_data, "sql")
    write_test_results("XSS Results:", xss_result_data, "xss")

    # Risk Analysis
    sqlPassed = sql_result_data.get('num_passed', 0)
    sqlFailed = sql_result_data.get('num_failed', 0)
    xssPassed = xss_result_data.get('num_passed', 0)
    xssFailed = xss_result_data.get('num_failed', 0)

    totalPassed = sqlPassed + xssPassed
    totalTests = totalPassed + sqlFailed + xssFailed
    ratio = (totalPassed / totalTests) * 100 if totalTests > 0 else 0

    if ratio <= 40:
        finalRating = " High Security Risk [0% - 40% Tests Passed]"
        emojiAnalysis = SOS_EMOJI
    elif ratio <= 69:
        finalRating = " Medium Security Risk [41% - 69% Tests Passed]"
        emojiAnalysis = MED_EMOJI
    elif ratio <= 99:
        finalRating = " Low Security Risk [70% - 99% Tests Passed]"
        emojiAnalysis = LOW_EMOJI
    else:
        finalRating = " No Security Risk [100% Tests Passed]"
        emojiAnalysis = NO_EMOJI

    height = check_space_needed(height, 30)
    file.setFont("Times-Bold", 20)
    file.drawString(50, height, "Final Risk Analysis:")
    height -= 30
    file.drawImage(emojiAnalysis, 50, height - 5, width=20, height=20)
    file.setFont("Times-Roman", 17)
    file.drawString(70, height, safe_text(finalRating))

    file.save()
    return pdf_path
