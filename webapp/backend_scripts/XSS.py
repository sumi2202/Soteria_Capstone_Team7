import re
import json
import subprocess
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import current_app
from webapp.models import XSSResult
from datetime import datetime, UTC
from app import app #FOR TESTING, DELETE AFTER

#function for xss tests
def xss_testing(url):

    num_passed = 0  # number of tests passed (no vulnerability)
    num_failed = 0  # number of tests failed (found vulnerability)

    type_passed = []  # type of tests passed (no vulnerability)
    type_failed = []  # type of tests failed (found vulnerability)

    # Looking for all pages in the website
    all_cmd = ["xsser", "-u", url, "--Crawling", "--auto"]
    try:
        all_cmd_run = subprocess.run(all_cmd, capture_output=True, text=True, timeout=800)
        url_list = re.findall(r"https?://[^\s'\"]+", all_cmd_run.stdout)
        url_list = list(set(url_list))  # getting a unique listing
    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {
            "type_failed": type_failed
        }

    # No extra pages found
    if not url_list:
        url_list = [url]


    # Running Testing for each url in the website
    for page in url_list:

        # using xsser tool to run XSS detection testing
        cmd = ["xsser", "-u", page, "--auto"]


        try:
            #Running xsser
            run = subprocess.run(cmd, capture_output=True, text=True, timeout= 800)
            test_result = run.stdout.lower() #getting testing results and converting to lowercase

            # **Evaluating XSS tests**

            # Stored XSS
            if "stored xss" in test_result or "vulnerable: stored" in test_result:
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Stored XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stored XSS, Location: {page}")

            # Reflected XSS
            if "reflected xss" in test_result or "alert(" in test_result or "vulnerable: reflected" in test_result:
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Reflected XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Reflected XSS, Location: {page}")

            # DOM Based XSS
            if "dom xss" in test_result or "document.write" in test_result or "vulnerable: dom" in test_result:
                num_failed += 1
                type_failed.append(f"Vulnerability Found: DOM Based XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"DOM Based XSS, Location: {page}")

        except Exception as e:
            type_failed.append(f"Error running tests: {str(e)}, Location: {page}")
            continue


    # Getting Time of Test Completion
    timestamp = datetime.now(UTC)

    #Listing out test results in JSON format
    result_analysis = {
        "url": url,
        "num_passed": num_passed,
        "num_failed": num_failed,
        "type_passed": type_passed,
        "type_failed": type_failed,
        "timestamp": timestamp
    }

    # ** Insert result_analysis into database, table xss_results **
    xss_result_analysis = XSSResult(current_app.db)
    xss_result_analysis.store_xssresult(result_analysis)

    return None


#FOR TESTING ONLY, DELETE AFTER
if __name__ == "__main__":

    with app.app_context():
        url_input = input("Enter the URL to test (XSS TESTING): ")
        xss_testing(url_input)