from flask import Flask
from .auth import auth
from .views import views
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhfbdbfjksd hfjksdkjdh'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth)


    return app