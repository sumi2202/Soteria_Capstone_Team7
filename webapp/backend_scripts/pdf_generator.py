from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from app import app  # FOR TESTING, DELETE AFTER

# This function takes the testing result data from the db and formats it into a downloadable pdf
def pdf_converter(url):

    db = current_app.db  # connect to database

    # Register font for emojis
    pdfmetrics.registerFont(TTFont('Symbola', '../static/assets/fonts/Symbola_hint.ttf'))

    # Getting most recent result data
    sql_result_data = db.sql_result.find_one({"url": url}, sort=[("timestamp", -1)])
    xss_result_data = db.xss_result.find_one({"url": url}, sort=[("timestamp", -1)])

    # Proceed only if there are results for the URL
    if sql_result_data and xss_result_data:
        w, h = A4  # Width & height of PDF
        file = canvas.Canvas("Soteria_Results.pdf", pagesize=A4)  # Define canvas with filename & size

        def check_space_needed(remaining_space, needed_space):
            """Check if there's enough space left on the current page. If not, start a new page."""
            if remaining_space < needed_space:
                file.showPage()  # Start a new page
                add_header()
                return h - 130  # Reset height after header
            return remaining_space

        def add_header():
            """Add the report header on each page."""
            file.drawImage("../static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65)
            file.setFont("Times-Roman", 20)
            file.drawString(w / 3, h - 90, "Soteria Testing Overview")

        # Add first header
        add_header()

        # Top details section (URL & timestamp)
        file.setFont("Times-Roman", 13)
        file.drawString(50, h - 130, f"URL: {url}")
        file.drawString(50, h - 150, f"Time of Completion: {xss_result_data.get('timestamp')}")

        height = h - 180  # Initial height

        # Function to write test results dynamically
        def write_test_results(title, data, category):
            """Writes the test results section dynamically and handles pagination."""
            nonlocal height

            file.setFont("Times-Roman", 16)
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

            height -= 10  # Space before failed section
            file.drawString(50, height, f"Failed Tests: {data.get('num_failed', 0)}")
            height -= 20

            for j in data.get("type_failed", []):
                height = check_space_needed(height, 15)
                file.drawString(70, height, f"--> {j}")
                height -= 15

            height -= 20  # Space before next section

        # Writing SQL and XSS results
        write_test_results("SQL Injection Results:", sql_result_data, "sql")
        write_test_results("XSS Results:", xss_result_data, "xss")

        # Final Risk Analysis Calculation
        sqlPassed = sql_result_data.get('num_passed')
        sqlFailed = sql_result_data.get('num_failed')
        xssPassed = xss_result_data.get('num_passed')
        xssFailed = xss_result_data.get('num_failed')
        totalPassed = sqlPassed + xssPassed
        totalTests = totalPassed + sqlFailed + xssFailed

        ratio = (totalPassed / totalTests) * 100

        if ratio <= 40:
            finalRating = "High Security Risk [⚠️ 0% - 40% Tests Passed]"
        elif ratio <= 69:
            finalRating = "Medium Security Risk [⚠️ 41% - 69% Tests Passed]"
        elif ratio <= 99:
            finalRating = "Low Security Risk [✅ 70% - 99% Tests Passed]"
        else:
            finalRating = "No Security Risk [✅ 100% Tests Passed]"

        # Displaying Final Risk Analysis
        file.setFont("Times-Roman", 16)
        height = check_space_needed(height, 30)
        file.drawString(50, height, "Final Risk Analysis:")
        height -= 30

        file.setFont("Symbola", 14)
        height = check_space_needed(height, 20)
        file.drawString(50, height, finalRating)

        file.save()

# FOR TESTING DELETE
if __name__ == "__main__":
    with app.app_context():
        url_input = input("Enter the URL to fetch results for: ")
        pdf_converter(url_input)
