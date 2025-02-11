
# Right now it displays the test results in a JSON format that contains:
# - Number of failed & passed tests
# - Types of failed & passed tests


import re
import subprocess
from flask import current_app
from ..models import SQLResult
import json

#function for sql injection tests
def sql_injection(url):

    num_passed = 0 #number of tests passed (no vulnerability)
    num_failed = 0 #number of tests failed (found vulnerability)

    type_passed = [] #type of tests passed (no vulnerability)
    type_failed = [] #type of tests failed (found vulnerability)

    #sqlmap command security tool, using the highest risk and level of tests
    cmd = ["sqlmap", "-u", url, "--batch", "--dbs", "--tamper=space2comment,charencode", "--random-agent", "--level=5", "--risk=3"]


    try:
        #Running sqlmap
        run = subprocess.run(cmd, capture_output=True, text=True, timeout= 800)
        test_result = run.stdout

        # **Evaluating SQl injection tests**

        #Boolean Based
        if "1=1" in test_result and "AND" in test_result:
            num_failed += 1
            type_failed.append("Vulnerability Found: Boolean-based Blind SQL Injection")
        else:
            num_passed += 1
            type_passed.append("Boolean-based Blind SQL Injection")

        #Union based
        if "union" in test_result.lower():
            num_failed += 1
            type_failed.append("Vulnerability Found: Union-based SQL Injection")
        else:
            num_passed += 1
            type_passed.append("Union-based SQL Injection")

        #Error based
        if "error" in test_result.lower():
            num_failed += 1
            type_failed.append("Vulnerability Found: Error-based SQL Injection")
        else:
            num_passed += 1
            type_passed.append("Error-based SQL Injection")

        #Time based
        if "sleep" in test_result.lower():
            num_failed += 1
            type_failed.append("Vulnerability Found: Time-based Blind SQL Injection")
        else:
            num_passed += 1
            type_passed.append("Time-based Blind SQL Injection")

        #Stacked Queries
        if "stacked queries" in test_result.lower() or ";" in test_result:
            num_failed += 1
            type_failed.append("Vulnerability Found: Stacked Queries SQL Injection")
        else:
            num_passed += 1
            type_passed.append("Stacked Queries SQL Injection")


        # ** Listing out found Databases **
        database_extract = re.findall(r"available databases \[.*?\]:\n\[(.*?)\]", test_result, re.DOTALL) #getting output from sqlmap command
        database_list = [name.strip() for name in database_extract[0].split(",")] if database_extract else [] #formating the string of multiple databases into a list

        #Listing out test results in JSON format
        result_analysis = {
            "url": url,
            "num_passed": num_passed,
            "num_failed": num_failed,
            "type_passed": type_passed,
            "type_failed": type_failed,
            "database_list": database_list
        }

        # ** Insert result_analysis into database, table sql_results **
        sql_result_analysis = SQLResult(current_app.db)
        sql_result_analysis.store_sqlresult(result_analysis)

        return None

    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {
            "type_failed": type_failed
        }







    