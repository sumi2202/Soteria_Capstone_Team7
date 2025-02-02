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
