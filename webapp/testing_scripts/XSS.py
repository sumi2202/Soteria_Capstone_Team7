import re
import json
import subprocess
from pymongo import MongoClient  #MongoDB

#function for xss tests
def xss_testing(url):

    num_passed = 0  # number of tests passed (no vulnerability)
    num_failed = 0  # number of tests failed (found vulnerability)

    type_passed = []  # type of tests passed (no vulnerability)
    type_failed = []  # type of tests failed (found vulnerability)

    # sqlmap library command, running xss technique
    cmd = ["sqlmap", "-u", url, "--batch", "--technique=X", "--random-agent"]


    try:
        #Running sqlmap
        run = subprocess.run(cmd, capture_output=True, text=True, timeout= 800)
        test_result = run.stdout

        # **Evaluating XSS tests**

        # Stored XSS
        if "stored XSS" in test_result.lower():
            num_failed += 1
            type_failed.append("Vulnerability Found: Stored XSS")
        else:
            num_passed += 1
            type_passed.append("Stored XSS")

        # Reflected XSS
        if "XSS" in test_result or "alert(" in test_result:
            num_failed += 1
            type_failed.append("Vulnerability Found: Reflected XSS")
        else:
            num_passed += 1
            type_passed.append("Reflected XSS")

        # DOM Based XSS
        if "DOM XSS" in test_result or "document.write" in test_result:
            num_failed += 1
            type_failed.append("Vulnerability Found: DOM Based XSS")
        else:
            num_passed += 1
            type_passed.append("DOM Based XSS")


        #Listing out test results in JSON format
        result_analysis = {
            "url": url,
            "num_passed": num_passed,
            "num_failed": num_failed,
            "type_passed": type_passed,
            "type_failed": type_failed,
        }

        # ** Insert result_analysis into database, table sql_results **



        return result_analysis

    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {
            "type_failed": type_failed
        }