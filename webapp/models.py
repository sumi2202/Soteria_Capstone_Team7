from flask import Flask, jsonify
from pymongo import MongoClient


class User:
    def signup(self):
        user = {
            "_id": "",
            "firstName": "",
            "lastName": "",
            "email":"",
            "password":""

        }
        return jsonify(user), 200
