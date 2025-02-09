from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


class User:
    def __init__(self, db):
        self.db = db
    def signup(self, first_name, last_name, email, password):
        user = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password

        }
        result = self.db.users.insert_one(user)
        return str(result.inserted_id)

class URLRegistration:
    def __init__(self, db):
        self.db = db
    def store_url(self, email, url, firstName, lastName, id_document, ownership_document, verified):
        url_entry = {
            "email": email,
            "url": url,
            "firstName": firstName,
            "lastName": lastName,
            "id_document": id_document,
            "ownership_document": ownership_document,
            "verified": verified,
        }
        result = self.db.URL_Registration.insert_one(url_entry)
        return str(result.inserted_id)
