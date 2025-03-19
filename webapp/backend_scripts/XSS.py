import re
import json
import subprocess
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import current_app
from playwright.sync_api import sync_playwright
from webapp.models import XSSResult
from datetime import datetime, UTC
from urllib.parse import urlparse
import emoji
#from app import app #FOR TESTING, DELETE AFTER

#function for xss tests
def xss_testing(url):
    print(f"[-->] Initiating Cross Site Scripting Testing on: {url}")

    # This ensures that only the pages only belonging to the urls domain is tested
    def check_domain(url2):
        originalDomain = urlparse(url).netloc
        return urlparse(url2).netloc == originalDomain

    num_passed = 0  # number of tests passed (no vulnerability)
    num_failed = 0  # number of tests failed (found vulnerability)

    type_passed = []  # type of tests passed (no vulnerability)
    type_failed = []  # type of tests failed (found vulnerability)

    # Function to crawl in order to find all additional pages within website
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

    # Taking out any additional pages that don't belong to the original domain
    filteredURLs = [url3 for url3 in url_list if check_domain(url3)]

    # No extra pages found
    if not filteredURLs:
        filteredURLs = [url]

    print(f"[-->] Verification complete, testing a total of {len(filteredURLs)} page(s)")

    # Running Testing for each url in the website
    for page in filteredURLs:
        print(f"[-->] Started Testing on page: {page}")
        # using xsser tool to run XSS detection testing
        cmd = ["xsser", "-u", page, "--auto"]


        try:
            #Running xsser
            print(f"[-->] Executing xsser on {page} ... Please wait.")
            run = subprocess.run(cmd, capture_output=True, text=True, timeout= 800)
            #print("[-->] Raw Output from xsser:")
            #print(run.stdout)
            test_result = run.stdout.lower() #getting testing results and converting to lowercase

            # **Evaluating XSS tests**
            print("[-->] Analyzing Test Results...")

            # Stored XSS
            if "stored xss" in test_result or "vulnerable: stored" in test_result:
                num_failed += 1
                type_failed.append(f"Stored XSS, Location: {page}")
                print(f"[!!] Stored XSS found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stored XSS, Location: {page}")

            # Reflected XSS
            if "reflected xss" in test_result or "alert(" in test_result or "vulnerable: reflected" in test_result:
                num_failed += 1
                type_failed.append(f"Reflected XSS, Location: {page}")
                print(f"[!!] Reflected XSS found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Reflected XSS, Location: {page}")

            # DOM Based XSS
            if "dom xss" in test_result or "document.write" in test_result or "vulnerable: dom" in test_result:
                num_failed += 1
                type_failed.append(f"DOM Based XSS, Location: {page}")
                print(f"[!!] DOM Based XSS found on: {page}")
            else:
                num_passed += 1
                type_passed.append(f"DOM Based XSS, Location: {page}")

        except Exception as e:
            print(f"[X] Error running tests on {page}: {str(e)}")
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
    #xss_result_analysis = XSSResult(current_app.db)
    #xss_result_analysis.store_xssresult(result_analysis)

    print("\U00002705 Cross Site Scripting Testing has been Completed!")

    return result_analysis


#FOR TESTING ONLY, DELETE AFTER
if __name__ == "__main__":
    from app import app
    with app.app_context():
        url_input = input("Enter the URL to test (XSS TESTING): ")
        xss_testing(url_input)