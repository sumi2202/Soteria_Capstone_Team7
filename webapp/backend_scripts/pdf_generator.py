from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app import app  # FOR TESTING, DELETE AFTER

# This function takes the testing result data from the db and formats it into a downloadable pdf
def pdf_converter(url):

    db = current_app.db  # connect to database

    # Getting most recent result data
    sql_result_data = db.sql_result.find_one({"url": url}, sort=[("timestamp", -1)])
    xss_result_data = db.xss_result.find_one({"url": url}, sort=[("timestamp", -1)])

    # Proceed only if there are results for the URL
    if sql_result_data and xss_result_data:
        w, h = A4  # pdf width and hieght
        file = canvas.Canvas("Soteria_Results.pdf", pagesize=A4)  # Define canvas with filename & size

        def check_space_needed(remaining_space, needed_space):
            if remaining_space < needed_space: #checking if we need a new page (no space left)
                file.showPage()  #creating a new page
                file.drawImage("../static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65) #adding logo for new page
                file.setFont("Times-Roman", 14)
                return h - 130
            return remaining_space


        # logo and title of the report
        file.drawImage("../static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65)
        file.setFont("Times-Bold", 20)
        file.drawString(w / 3, h - 90, "Soteria Testing Overview")

        #displaying URL and testing timestamp
        file.setFont("Times-Bold", 13)
        file.drawString(50, h - 130, f"URL: ")
        file.setFont("Times-Roman", 13)
        file.drawString(85, h - 130, f"{url}") #associated url for the result report

        file.setFont("Times-Bold", 13)
        file.drawString(50, h - 150, f"Time of Completion: ")
        file.setFont("Times-Roman", 13)  #associated timestamp
        file.drawString(170, h - 150, f"{xss_result_data.get('timestamp')}")

        height = h - 180

        # Function to write test results dynamically
        def write_test_results(title, data, category):
            nonlocal height

            file.setFont("Times-Bold", 16)
            height = check_space_needed(height, 30)
            file.drawString(50, height, title)
            height -= 30

            file.setFont("Times-Roman", 14)
            file.drawString(50, height, f"Passed Tests: {data.get('num_passed', 0)}")
            height -= 20 #blank space

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

            height -= 20 #blank space

            if category == "sql":
                file.drawString(50, height, f"Detected Databases:")
                height -= 20

                for j in data.get("database_list", []):
                    height = check_space_needed(height, 15)
                    file.drawString(70, height, f"--> {j}")
                    height -= 15

                height -= 20 #blank space

        # SQL and XSS result listings
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
            finalRating = " High Security Risk [0% - 40% Tests Passed]"
            emojiAnalysis = "../static/assets/sos.png" #emoji to be displayed depending on risk analysis
        elif ratio <= 69:
            finalRating = " Medium Security Risk [41% - 69% Tests Passed]"
            emojiAnalysis = "../static/assets/med.png"  # emoji to be displayed depending on risk analysis
        elif ratio <= 99:
            finalRating = " Low Security Risk [70% - 99% Tests Passed]"
            emojiAnalysis = "../static/assets/low.png"  # emoji to be displayed depending on risk analysis
        else:
            finalRating = " No Security Risk [100% Tests Passed]"
            emojiAnalysis = "../static/assets/no.png"  # emoji to be displayed depending on risk analysis

        height -= 20

        # Displaying Final Risk Analysis
        file.setFont("Times-Bold", 20)
        height = check_space_needed(height, 30)
        file.drawString(50, height, "Final Risk Analysis:")
        height -= 30

        file.drawImage(emojiAnalysis, 50, height - 5, width=20, height=20) #emoji
        file.setFont("Times-Roman", 17)
        height = check_space_needed(height, 20)
        file.drawString(70, height, finalRating) #result string



        file.save()

# FOR TESTING DELETE
if __name__ == "__main__":
    with app.app_context():
        url_input = input("Enter the URL to fetch results for: ")
        pdf_converter(url_input)
