import re
import subprocess
from flask import current_app
from ..models import SQLResult
from datetime import datetime, UTC

#function for sql injection tests
def sql_injection(url):

    num_passed = 0 #number of tests passed (no vulnerability)
    num_failed = 0 #number of tests failed (found vulnerability)

    type_passed = [] #type of tests passed (no vulnerability)
    type_failed = [] #type of tests failed (found vulnerability)

    database_list = [] #list of databases found

    #Looking for all pages in the website
    all_cmd = ["sqlmap", "-u", url, "--crawl=4", "--batch"]
    try:
        all_cmd_run = subprocess.run(all_cmd, capture_output=True, text=True, timeout= 800)
        url_list = re.findall(r"https?://[^\s'\"]+", all_cmd_run.stdout)
        url_list = list(set(url_list)) #getting a unique listing
    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {
            "type_failed": type_failed
        }

    #No extra pages found
    if not url_list:
        url_list = [url]


    #Running Testing for each url in the website
    for page in url_list:

        #sqlmap command security tool, using the highest risk and level of tests
        cmd = ["sqlmap", "-u", page, "--batch", "--dbs", "--tamper=space2comment,charencode", "--random-agent", "--level=5", "--risk=3"]

        try:
            #Running sqlmap
            run = subprocess.run(cmd, capture_output=True, text=True, timeout= 800)
            test_result = run.stdout #output of tests

            # **Evaluating SQl injection tests**

            #Boolean Based
            if "1=1" in test_result and "AND" in test_result:
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Boolean-based Blind SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Boolean-based Blind SQL Injection, Location: {page}")

            #Union based
            if "union" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Union-based SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Union-based SQL Injection, Location: {page}")

            #Error based
            if "error" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Error-based SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Error-based SQL Injection, Location: {page}")

            #Time based
            if "sleep" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Time-based Blind SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Time-based Blind SQL Injection, Location: {page}")

            #Stacked Queries
            if "stacked queries" in test_result.lower() or ";" in test_result:
                num_failed += 1
                type_failed.append(f"Vulnerability Found: Stacked Queries SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stacked Queries SQL Injection, Location: {page}")


            # ** Listing out found Databases **
            database_extract = re.findall(r"available databases \[.*?\]:\n\[(.*?)\]", test_result, re.DOTALL) #getting output from sqlmap command
            if database_extract: #if databases are found
                current_database_list = [name.strip() for name in database_extract[0].split(",")] #formating the string of multiple databases into a list
                database_list.extend(current_database_list) #append found databases to final listing
                database_list = list(set(database_list))  # getting a unique listing
            else: #if no databases are found, skip
                pass


        except Exception as e:
            type_failed.append(f"Error running tests: {str(e)}, Location: {page}")
            continue

    #Getting Time of Test Completion
    timestamp = datetime.now(UTC)

    #Listing out test results in JSON format
    result_analysis = {
        "url": url,
        "num_passed": num_passed,
        "num_failed": num_failed,
        "type_passed": type_passed,
        "type_failed": type_failed,
        "database_list": database_list,
        "timestamp": timestamp,
    }

    # ** Insert result_analysis into database, table sql_results **
    sql_result_analysis = SQLResult(current_app.db)
    sql_result_analysis.store_sqlresult(result_analysis)

    return None





    