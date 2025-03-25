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
def xss_testing(url, progress_callback=None):
    print(f"[-->] Initiating Cross Site Scripting Testing on: {url}")

    def check_domain(url2):
        originalDomain = urlparse(url).netloc
        return urlparse(url2).netloc == originalDomain

    num_passed = 0
    num_failed = 0
    type_passed = []
    type_failed = []

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
            progress_callback(25)
    except Exception as e:
        type_failed.append(f"Error running tests {str(e)}")
        return {"type_failed": type_failed}

    filteredURLs = [url3 for url3 in url_list if check_domain(url3)]
    if not filteredURLs:
        filteredURLs = [url]

    print(f"[-->] Testing {len(filteredURLs)} page(s)...")
    for i, page in enumerate(filteredURLs):
        print(f"[-->] Testing page: {page}")
        cmd = ["xsser", "-u", page, "--auto"]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=800)
            test_result = run.stdout.lower()

            if "stored xss" in test_result or "vulnerable: stored" in test_result:
                num_failed += 1
                type_failed.append(f"Stored XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Stored XSS, Location: {page}")

            if "reflected xss" in test_result or "alert(" in test_result or "vulnerable: reflected" in test_result:
                num_failed += 1
                type_failed.append(f"Reflected XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"Reflected XSS, Location: {page}")

            if "dom xss" in test_result or "document.write" in test_result or "vulnerable: dom" in test_result:
                num_failed += 1
                type_failed.append(f"DOM Based XSS, Location: {page}")
            else:
                num_passed += 1
                type_passed.append(f"DOM Based XSS, Location: {page}")

        except Exception as e:
            type_failed.append(f"Error running tests: {str(e)}, Location: {page}")
            continue

        if progress_callback:
            progress_callback(25 + int((i + 1) / len(filteredURLs) * 25))  # 25 → 50

    timestamp = datetime.now(UTC)
    result_analysis = {
        "url": url,
        "num_passed": num_passed,
        "num_failed": num_failed,
        "type_passed": type_passed,
        "type_failed": type_failed,
        "timestamp": timestamp,
        "task_id": ""
    }

    if progress_callback:
        progress_callback(50)

    print("\U00002705 Cross Site Scripting Testing has been Completed!")
    return result_analysis



#FOR TESTING ONLY, DELETE AFTER
if __name__ == "__main__":
    from app import app
    with app.app_context():
        url_input = input("Enter the URL to test (XSS TESTING): ")
        xss_testing(url_input)