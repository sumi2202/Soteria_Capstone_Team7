
# Returns two integers:
# - Does the URL exist? (0 = Yes, 1 = No)
# - Is the URL available? (0 = Yes, 1 = No)


import validators #package used to check for URL formatting
import requests #package used to check if URL exists
from pymongo import MongoClient  #MongoDB

#Connect to database
client = MongoClient('mongodb://10.190.37.194:27017/')
db = client['Crack_Database'] #database
table = db['URL Information'] #table


#both of these have to stay 0 for it to be validated
validURL = 0
alreadyRegistered = 0


def url_validation(email, url):
    validation = validators.url(url)

    if not validation: #invalid url
        validURL = 1
        alreadyRegistered = 1
        return validURL, alreadyRegistered

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        exists = requests.get(url, timeout=12, headers=headers, allow_redirects=True) #try to reach the URL for 12 seconds
        if exists.status_code == 200:

            #Check if the URL is already in the database with another user
            if table.find_one({"URL": url, "email": {"$ne": email}}) is not None:
                alreadyRegistered = 1

            else:
                # Check if the URL has already been submitted by the same user before
                if table.find_one({"URL": url, "email": email}) is not None:
                    alreadyRegistered = 0

                else:
                    # **Insert the URL and user in the db**
                    newEntry = {
                        "email": email,
                        "URL": url
                    }
                    #table.insert_one(newEntry)

                    alreadyRegistered = 0

        else:
            validURL = 1 #URL does not exist
    except requests.RequestException as errorMsg:
        validURL = 1 #URL not reached

    return validURL, alreadyRegistered