# Returns three integers:
# - Can the URL be reached? (0 = Yes, 1 = No)
# - Does the URL exist? (0 = Yes, 1 = No)
# - Is the URL available? (0 = Yes, 1 = No)

import validators  # package used to check for URL formatting
import requests  # package used to check if URL exists
from flask import current_app


def url_validation(email, url):
    print(f"🛠 [DEBUG] Inside url_validation → Email: {email}, URL: {url}")
    # These have to stay 0 for it to be validated
    validURL = 0
    invalidURL = 0
    alreadyRegistered = 0

    db = current_app.db  # connect to database

    validation = validators.url(url)
    if not validation:  # invalid url
        print("🚨 [DEBUG] Invalid URL format!")
        invalidURL = 1
        return validURL, invalidURL, alreadyRegistered

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        exists = requests.get(url, timeout=12, headers=headers,
                              allow_redirects=True)  # try to reach the URL for 12 seconds
        print(f"🔍 [DEBUG] URL Response Status Code: {exists.status_code}")

        if exists.status_code == 200:

            # Check if the URL is already in the database with another user
           exist_entry = db.users.find_one({"registered_url": url, "verified": True, "email":{"$ne": email}}) is not None  # url is found to be registered to another user, add "verified" field = true check
        if exist_entry:
            print("⚠️ [DEBUG] URL is already registered to another user!")
            alreadyRegistered = 1
        else:
            print("✅ [DEBUG] URL exists and is reachable!")
            validURL = 0

    except requests.RequestException as e:
        print(f"⚠️ [DEBUG] Request failed: {e}")
        validURL = 1  # URL not reached

    print(
        f"✅ [DEBUG] Final Results → validURL: {validURL}, invalidURL: {invalidURL}, alreadyRegistered: {alreadyRegistered}")
    return validURL, invalidURL, alreadyRegistered