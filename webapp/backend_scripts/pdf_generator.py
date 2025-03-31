from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def pdf_converter(url, task_id):
    db = current_app.db

    # Fetch latest results for the given URL
    sql_result_data = db.sql_result.find_one({"url": url}, sort=[("timestamp", -1)])
    xss_result_data = db.xss_result.find_one({"url": url}, sort=[("timestamp", -1)])

    if not sql_result_data or not xss_result_data:
        return None

    # Ensure the output folder exists
    os.makedirs("pdf_cache", exist_ok=True)
    pdf_path = f"pdf_cache/Soteria_Results_{task_id}.pdf"
    w, h = A4
    file = canvas.Canvas(pdf_path, pagesize=A4)

    def check_space_needed(remaining_space, needed_space):
        if remaining_space < needed_space:
            file.showPage()
            file.drawImage("static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65)
            file.setFont("Times-Roman", 14)
            return h - 130
        return remaining_space

    # Header
    file.drawImage("static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65)
    file.setFont("Times-Bold", 20)
    file.drawString(w / 3, h - 90, "Soteria Testing Overview")

    # URL and timestamp
    file.setFont("Times-Bold", 13)
    file.drawString(50, h - 130, "URL:")
    file.setFont("Times-Roman", 13)
    file.drawString(85, h - 130, url)

    file.setFont("Times-Bold", 13)
    file.drawString(50, h - 150, "Time of Completion:")
    file.setFont("Times-Roman", 13)
    file.drawString(170, h - 150, str(xss_result_data.get('timestamp')))

    height = h - 180

    # Helper to write result sections
    def write_test_results(title, data, category):
        nonlocal height
        file.setFont("Times-Bold", 16)
        height = check_space_needed(height, 30)
        file.drawString(50, height, title)
        height -= 30

        file.setFont("Times-Roman", 14)
        file.drawString(50, height, f"Passed Tests: {data.get('num_passed', 0)}")
        height -= 20
        for i in data.get("type_passed", []):
            height = check_space_needed(height, 15)
            file.drawString(70, height, f"--> {i}")
            height -= 15

        height -= 10
        file.drawString(50, height, f"Failed Tests: {data.get('num_failed', 0)}")
        height -= 20
        for j in data.get("type_failed", []):
            height = check_space_needed(height, 15)
            file.drawString(70, height, f"--> {j}")
            height -= 15

        if category == "sql":
            height -= 20
            file.drawString(50, height, "Detected Databases:")
            height -= 20
            for j in data.get("database_list", []):
                height = check_space_needed(height, 15)
                file.drawString(70, height, f"--> {j}")
                height -= 15

        height -= 20

    # Inject both test results
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
        emojiAnalysis = "static/assets/sos.png"
    elif ratio <= 69:
        finalRating = " Medium Security Risk [41% - 69% Tests Passed]"
        emojiAnalysis = "static/assets/med.png"
    elif ratio <= 99:
        finalRating = " Low Security Risk [70% - 99% Tests Passed]"
        emojiAnalysis = "static/assets/low.png"
    else:
        finalRating = " No Security Risk [100% Tests Passed]"
        emojiAnalysis = "static/assets/no.png"

    height = check_space_needed(height, 30)
    file.setFont("Times-Bold", 20)
    file.drawString(50, height, "Final Risk Analysis:")
    height -= 30
    file.drawImage(emojiAnalysis, 50, height - 5, width=20, height=20)
    file.setFont("Times-Roman", 17)
    file.drawString(70, height, finalRating)

    file.save()
    return pdf_path
