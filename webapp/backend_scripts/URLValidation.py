import validators
import requests
from flask import current_app

def url_validation(email, url):
    print(f"🛠 [DEBUG] Inside url_validation → Email: {email}, URL: {url}")

    # Default validation results
    validURL = 0
    invalidURL = 0
    alreadyRegistered = 0

    db = current_app.db

    # Validate URL format
    if not validators.url(url):
        print("🚨 [DEBUG] Invalid URL format!")
        invalidURL = 1
        return validURL, invalidURL, alreadyRegistered

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        response = requests.get(url, timeout=12, headers=headers, allow_redirects=True)

        print(f"🔍 [DEBUG] URL Response Status Code: {response.status_code}")

        if response.status_code == 200:
            # DEBUG: Print database content for verification
            print(f"📊 [DEBUG] Checking DB for URL: {url}")
            for entry in db.registered_urls.find({"url": url}):
                print(f"📌 [DEBUG] Found entry: {entry}")

            # Check if URL is already registered under a different email
            exist_entry = db.registered_urls.find_one({
                "url": url,  # ✅ FIXED field name
                "verified": True,
                "email": {"$ne": email}  # ✅ Ensures it's not the same user
            }) is not None

            if exist_entry:
                print("⚠️ [DEBUG] URL is already registered to another user!")
                alreadyRegistered = 1
            else:
                print("✅ [DEBUG] URL exists and is reachable!")
                validURL = 0

    except requests.RequestException as e:
        print(f"⚠️ [DEBUG] Request failed: {e}")
        validURL = 1

    print(f"✅ [DEBUG] Final Results → validURL: {validURL}, invalidURL: {invalidURL}, alreadyRegistered: {alreadyRegistered}")
    return validURL, invalidURL, alreadyRegistered