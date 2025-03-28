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


# from app import app #FOR TESTING, DELETE AFTER


# function for sql injection tests
# level values = 1,2,3,4,5
# risk values = 1,2,3
def sql_injection(url, level, risk, progress_callback=None):
    print(f"[-->] Initiating SQL Injection Testing on: {url}")

    num_passed = 0
    num_failed = 0
    type_passed = []
    type_failed = []
    database_list = []

    def check_domain(url2):
        originalDomain = urlparse(url).netloc
        return urlparse(url2).netloc == originalDomain

    def crawler(url):
        with sync_playwright() as p:
            firefox = p.chromium.launch(headless=True)
            websitePage = firefox.new_page()
            websitePage.goto(url)
            websitePage.wait_for_timeout(3000)
            url_listing = set()
            urls = [url]

            try:
                buttons = websitePage.query_selector_all("button")
                for i in range(len(buttons)):
                    try:
                        websitePage.goto(url)
                        websitePage.wait_for_timeout(3000)
                        buttons = websitePage.query_selector_all("button")
                        if i < len(buttons):
                            buttons[i].click()
                            websitePage.wait_for_timeout(3000)
                            new_url = websitePage.url
                            if check_domain(new_url) and new_url not in url_listing:
                                urls.append(new_url)
                    except Exception:
                        continue
            except Exception:
                pass

            while urls:
                current_url = urls.pop(0)
                if current_url in url_listing:
                    continue
                url_listing.add(current_url)

                websitePage.goto(current_url)
                websitePage.wait_for_timeout(3000)
                page_urls = websitePage.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
                for page in page_urls:
                    if check_domain(page) and page not in url_listing:
                        urls.append(page)

            firefox.close()
        return url_listing

    print("[-->] Crawling for additional pages...")
    try:
        url_list = crawler(url)
        url_list = list(set(url_list))
        print(f"[-->] Crawling Completed. Found {len(url_list)} potential pages to test...")
        if progress_callback:
            progress_callback(60)
    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {"type_failed": type_failed}

    filteredURLs = [url3 for url3 in url_list if check_domain(url3)]
    if not filteredURLs:
        filteredURLs = [url]

    print(f"[-->] Testing {len(filteredURLs)} page(s)...")
    for i, page in enumerate(filteredURLs):
        print(f"[-->] Testing page: {page}")
        cmd = ["sqlmap", "-u", page, "--batch", "--dbs", "--tamper=space2comment,charencode", "--random-agent",
               f"--level={level}", f"--risk={risk}", "--threads=3", "--time-sec=5"]
        try:
            #run = subprocess.run(cmd, capture_output=True, text=True, timeout=500)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                test_result, error_output = process.communicate(timeout=1600)
            except subprocess.TimeoutExpired:
                process.kill()
                test_result, error_output = process.communicate()
                type_failed.append(f"SQLMap test timed out after 1200 seconds, Location: {page}")
                continue

            #test_result = run.stdout.lower()
            test_result = test_result.lower()

            if "1=1" in test_result and "and" in test_result:
                num_failed += 1
                type_failed.append(f"Boolean-based Blind SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Boolean-based Blind SQL Injection, Location: {page}")

            if "union" in test_result:
                num_failed += 1
                type_failed.append(f"Union-based SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Union-based SQL Injection, Location: {page}")

            if "error" in test_result:
                num_failed += 1
                type_failed.append(f"Error-based SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Error-based SQL Injection, Location: {page}")

            if "sleep" in test_result:
                num_failed += 1
                type_failed.append(f"Time-based Blind SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Time-based Blind SQL Injection, Location: {page}")

            if "stacked queries" in test_result or ";" in test_result:
                num_failed += 1
                type_failed.append(f"Stacked Queries SQL Injection, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stacked Queries SQL Injection, Location: {page}")

            database_extract = re.findall(r"available databases.*?\]:\n(.*?)\n\n", test_result, re.DOTALL)
            if database_extract:
                current_database_list = [name.strip() for name in database_extract[0].split(",")]
                database_list.extend(current_database_list)
                database_list = list(set(database_list))
            else:
                database_list = ["No Databases Found"]

        except Exception as e:
            type_failed.append(f"Error running tests: {str(e)}, Location: {page}")
            continue

        if progress_callback:
            progress_callback(60 + int((i + 1) / len(filteredURLs) * 30))  # 60 → 90

    timestamp = datetime.now(UTC)
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

    if progress_callback:
        progress_callback(90)

    print("\U00002705 Cross Site Scripting Testing has been Completed!")
    return result_analysis

# #FOR TESTING ONLY, DELETE AFTER
# if __name__ == "__main__":
#
#     with app.app_context():
#         url_input = input("Enter the URL to test (SQLi TESTING): ")
#         sql_injection(url_input, 3, 2)





    