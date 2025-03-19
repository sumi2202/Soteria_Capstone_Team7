import re
import subprocess
import os
import sys
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import current_app
from webapp.models import SQLResult
from datetime import datetime, UTC
#from app import app #FOR TESTING, DELETE AFTER


#function for sql injection tests
#level values = 1,2,3,4,5
#risk values = 1,2,3
def sql_injection(url, level, risk):
    print(f"[-->] Initiating SQL Injection Testing on: {url}")

    num_passed = 0 #number of tests passed (no vulnerability)
    num_failed = 0 #number of tests failed (found vulnerability)

    type_passed = [] #type of tests passed (no vulnerability)
    type_failed = [] #type of tests failed (found vulnerability)

    database_list = [] #list of databases found


    #This ensures that only the pages only belonging to the urls domain is tested
    def check_domain(url2):
        originalDomain = urlparse(url).netloc
        return urlparse(url2).netloc == originalDomain

    #Function to crawl in order to find all additional pages within website
    def crawler(url):
        with sync_playwright() as p:
            firefox = p.chromium.launch(headless=True) #don't show as a popup
            websitePage = firefox.new_page()
            websitePage.goto(url)
            websitePage.wait_for_timeout(3000)
            url_listing = set()
            urls = [url]  #homepage of given url

            # **Get list of buttons before clicking**
            try:
                buttons = websitePage.query_selector_all("button") #looking for all the buttons
                button_count = len(buttons)
                print(f"[-->] Found {button_count} buttons on the page.")

                for i in range(button_count):
                    try:
                        print(f"[-->] Clicking button {i + 1}...")
                        websitePage.goto(url) # go back to homepage
                        websitePage.wait_for_timeout(3000)

                        buttons = websitePage.query_selector_all("button") #finding the next button
                        if i < len(buttons):  # Ensure the button still exists
                            buttons[i].click()
                            websitePage.wait_for_timeout(3000)  # Wait for potential navigation

                            new_url = websitePage.url
                            if check_domain(new_url) and new_url not in url_listing:
                                urls.append(new_url) #appending the new page to the url list
                                print(f"[-->] Found new page: {new_url}")

                        else:
                            print(f"[X] Button {i + 1} is no longer available.")

                    except Exception as e:
                        print(f"[X] Error clicking button {i + 1}: {e}")

            except Exception as e:
                print(f"[X] Error finding buttons: {e}")

            # **Crawling**
            while urls:
                current_url = urls.pop(0)

                if current_url in url_listing:
                    continue
                url_listing.add(current_url)

                websitePage.goto(current_url)
                websitePage.wait_for_timeout(3000)

                # Find all links on the page
                page_urls = websitePage.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
                for page in page_urls:
                    if check_domain(page) and page not in url_listing:
                        urls.append(page)

            firefox.close()
        return url_listing


    # Looking for all pages in the website
    print("[-->] Crawling for additional pages...")
    try:
        url_list = crawler(url)
        url_list = list(set(url_list))  # getting a unique listing
        print(f"[-->] Crawling Completed. Found {len(url_list)} potential pages to test...")
    except Exception as e:
        print(f"[X] Error during crawling: {str(e)}")
        type_failed.append(f"Error running tests {str(e)}")
        return {
            "type_failed": type_failed
        }

    print(f"[-->] Verifying additional pages...")

    #Taking out any additional pages that don't belong to the original domain
    filteredURLs = [url3 for url3 in url_list if check_domain(url3)]


    #No extra pages found
    if not filteredURLs:
        filteredURLs = [url]



    print(f"[-->] Verification complete, testing a total of {len(filteredURLs)} page(s)")

    #Running Testing for each url in the website
    for page in filteredURLs:
        print(f"[-->] Started Testing on page: {page}")
        #sqlmap command security tool, using the medium risk and level of tests
        cmd = ["sqlmap", "-u", page, "--batch", "--dbs", "--tamper=space2comment,charencode", "--random-agent", f"--level={level}", f"--risk={risk}", "--threads=5"]

        try:
            #Running sqlmap
            print(f"[-->] Executing SQLMap on {page} ... Please wait.")
            run = subprocess.run(cmd, capture_output=True, text=True, timeout= 500)
            test_result = run.stdout #output of tests

            # **Evaluating SQl injection tests**
            print("[-->] Analyzing Test Results...")

            #Boolean Based
            if "1=1" in test_result and "AND" in test_result:
                num_failed += 1
                type_failed.append(f"Boolean-based Blind SQL Injection, Location: {page}")
                print(f"[!!] Boolean-based SQL Injection found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Boolean-based Blind SQL Injection, Location: {page}")

            #Union based
            if "union" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Union-based SQL Injection, Location: {page}")
                print(f"[!!] Union-based SQL Injection found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Union-based SQL Injection, Location: {page}")

            #Error based
            if "error" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Error-based SQL Injection, Location: {page}")
                print(f"[!!] Error-based SQL Injection found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Error-based SQL Injection, Location: {page}")

            #Time based
            if "sleep" in test_result.lower():
                num_failed += 1
                type_failed.append(f"Time-based Blind SQL Injection, Location: {page}")
                print(f"[!!] Time-based SQL Injection found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Time-based Blind SQL Injection, Location: {page}")

            #Stacked Queries
            if "stacked queries" in test_result.lower() or ";" in test_result:
                num_failed += 1
                type_failed.append(f"Stacked Queries SQL Injection, Location: {page}")
                print(f"[!!] Stacked Queries SQL Injection found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stacked Queries SQL Injection, Location: {page}")


            # ** Listing out found Databases **
            database_extract = re.findall(r"available databases.*?\]:\n(.*?)\n\n", test_result, re.DOTALL)
             #getting output from sqlmap command
            if database_extract: #if databases are found
                current_database_list = [name.strip() for name in database_extract[0].split(",")] #formating the string of multiple databases into a list
                database_list.extend(current_database_list) #append found databases to final listing
                database_list = list(set(database_list))  # getting a unique listing
                print(f"[-->] List of Databases found: {', '.join(database_list)}")
            else: #if no databases are found, skip
                database_list = ["No Databases Found"]
                pass


        except Exception as e:
            print(f"[X] Error running tests on {page}: {str(e)}")
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
        "task_id": ""
    }

    # ** Insert result_analysis into database, table sql_results **
    #sql_result_analysis = SQLResult(current_app.db)
    #sql_result_analysis.store_sqlresult(result_analysis)

    print("\U00002705 SQL Injection Testing has been Completed!")

    return result_analysis


#FOR TESTING ONLY, DELETE AFTER
if __name__ == "__main__":

    with app.app_context():
        url_input = input("Enter the URL to test (SQLi TESTING): ")
        sql_injection(url_input, 3, 2)


    