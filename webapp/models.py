from flask import Flask, jsonify, session
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
            "notified": False,
        }
        result = self.db.URL_Registration.insert_one(url_entry)
        return str(result.inserted_id)


class SQLResult:
    def __init__(self, db):
        self.db = db
    def store_sqlresult(self, result_analysis):
        result = self.db.sql_result.insert_one(result_analysis)
        return str(result.inserted_id)


class XSSResult:
    def __init__(self, db):
        self.db = db
    def store_xssresult(self, result_analysis):
        result = self.db.xss_result.insert_one(result_analysis)
        return str(result.inserted_id)


class Rating:
    def __init__(self, db):
        self.db = db
    def store_rating(self, sessionC, rating):
        rating_entry = {
            "sessionC": sessionC,
            "rating": rating
        }
        result = self.db.customer_rating.insert_one(rating_entry)
        return str(result.inserted_id)