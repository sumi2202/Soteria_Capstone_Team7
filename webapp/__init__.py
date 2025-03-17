from flask import Flask
from pymongo import MongoClient
from gridfs import GridFS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhfbdbfjksd hfjksdkjdh'
    app.secret_key = 'SOFECapstone2425'

    app.config['MONGO_URI'] = 'mongodb+srv://SoteriaUser:SOFEcapstone2425@soteriacluster.g7txq.mongodb.net/'
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.soteria

    app.fs = GridFS(app.db)
    with app.app_context():
        fs = GridFS(app.db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth)

    return app
