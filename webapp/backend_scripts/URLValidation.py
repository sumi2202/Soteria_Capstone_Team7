# Returns three integers:
# - Can the URL be reached? (0 = Yes, 1 = No)
# - Does the URL exist? (0 = Yes, 1 = No)
# - Is the URL available? (0 = Yes, 1 = No)

import validators  # package used to check for URL formatting
import requests  # package used to check if URL exists
from flask import current_app


def url_validation(email, url):
    print(f"🛠 [DEBUG] Inside url_validation → Email: {email}, URL: {url}")
    validURL = 1  # Default to invalid URL (1) until proven otherwise
    invalidURL = 0
    alreadyRegistered = 0

    db = current_app.db  # connect to database

    # Check if the URL format is valid with a protocol (https:// or http://)
    validation = validators.url(url)  # Don't prepend 'http://' here, check only for valid URLs with a protocol
    if not validation:  # If URL is not valid, treat it as invalid
        print("🚨 [DEBUG] Invalid URL format!")
        validURL = 1  # Treat it as invalid
        return validURL, invalidURL, alreadyRegistered

    try:
        # Now, check if the URL is reachable
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        exists = requests.get(url, timeout=12, headers=headers, allow_redirects=True)  # Try to reach the URL for 12 seconds
        print(f"🔍 [DEBUG] URL Response Status Code: {exists.status_code}")

        if exists.status_code == 200:
            # Check if the URL is already in the database with another user (other than the current one)
            exist_entry = db.URL_Registration.find_one({"url": url, "verified": True, "email": {"$ne": email}}) is not None
            if exist_entry:
                print("⚠️ [DEBUG] URL is already registered to another user!")
                alreadyRegistered = 1
            else:
                print("✅ [DEBUG] URL exists and is reachable!")
                validURL = 0  # URL is reachable and available

        else:
            # URL status code is not 200, meaning URL doesn't exist or is unreachable
            validURL = 1  # Treat it as not reachable (does not exist)

    except requests.RequestException as e:
        print(f"⚠️ [DEBUG] Request failed: {e}")
        validURL = 1  # URL not reached

    print(f"✅ [DEBUG] Final Results → validURL: {validURL}, invalidURL: {invalidURL}, alreadyRegistered: {alreadyRegistered}")
    return validURL, invalidURL, alreadyRegistered