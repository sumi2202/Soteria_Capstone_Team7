from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app import app #FOR TESTING, DELETE AFTER


#This function takes the testing result data from the db and formats it into a downloadable pdf
def pdf_converter(url):

    db = current_app.db  # connect to database

    #Getting most recent result data
    sql_result_data = db.sql_result.find_one({"url": url}, sort=[("timestamp", -1)])
    xss_result_data = db.sql_result.find_one({"url": url}, sort=[("timestamp", -1)])

    #proceed only if there are results for the url
    if sql_result_data and xss_result_data:

        w, h = A4 #width & height of pdf
        file = canvas.Canvas("Soteria_Results.pdf", pagesize=A4) #defining canvas with filename & size

        #Soteria logo
        file.drawImage("../static/assets/Soteria_logo_white.png", 40, h - 80, width=65, height=65)

        #Title of report
        file.setFont("Times-Roman", 20)
        file.drawString(w/3, h - 90,"Soteria Testing Overview")

        #Top details section (url & timestamp)
        file.setFont("Times-Roman", 13)
        file.drawString(50, h - 130, f"URL: {url}")
        file.drawString(50, h - 150, f"Time of Completion: {xss_result_data.get('timestamp')}")


        #SQLi Result Listing
        file.setFont("Times-Roman", 16)
        file.drawString(50, h - 190, "SQL Injection Results:")

        #Passed SQLi Test Details
        file.setFont("Times-Roman", 14)
        file.drawString(50, h - 220, f"Passed Tests: {sql_result_data.get('num_passed', 0)}")
        height = h - 240
        for i in sql_result_data.get("type_passed", []):
            file.drawString(70, height, f"--> {i}")
            height -= 15

        #Failed SQLi Listing
        file.setFont("Times-Roman", 14)
        file.drawString(50, height - 25, f"Failed Tests: {sql_result_data.get('num_failed', 0)}")
        height = height - 45
        for j in sql_result_data.get("type_failed", []):
            file.drawString(70, height, f"--> {j}")
            height -= 15




        #XSS Result Listing
        file.setFont("Times-Roman", 16)
        file.drawString(50, height - 30, "XSS Results:")

        #Passed XSS Test Details
        file.setFont("Times-Roman", 14)
        file.drawString(50, height - 60, f"Passed Tests: {xss_result_data.get('num_passed', 0)}")
        height = height - 80
        for i in xss_result_data.get("type_passed", []):
            file.drawString(70, height, f"--> {i}")
            height -= 15

        #Failed XSS Listing
        file.setFont("Times-Roman", 14)
        file.drawString(50, height - 25, f"Failed Tests: {xss_result_data.get('num_failed', 0)}")
        height = height - 45
        for j in xss_result_data.get("type_failed", []):
            file.drawString(70, height, f"--> {j}")
            height -= 15


        file.save()


#FOR TESTING DELETE
if __name__ == "__main__":

    with app.app_context():
        url_input = input("Enter the URL to fetch results for: ")
        pdf_converter(url_input)


