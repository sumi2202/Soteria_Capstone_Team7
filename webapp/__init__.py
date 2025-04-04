from flask import Flask
from pymongo import MongoClient
from gridfs import GridFS
from .models import SQLResult, XSSResult
from .test_routes import check_verified_links
from .extensions import socketio
import threading


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhfbdbfjksd hfjksdkjdh'
    app.secret_key = 'SOFECapstone2425'
    app.config['MONGO_URI'] = 'mongodb+srv://SoteriaUser:SOFEcapstone2425@soteriacluster.g7txq.mongodb.net/'

    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database('soteria')
    db = app.db

    def start_verified_link_thread():
        thread = threading.Thread(target=check_verified_links, args=(app,), daemon=True)
        thread.start()
        print("[INIT] 🔁 Background thread to check verified links started.")

    start_verified_link_thread()

    # Register indexes
    def create_indexes(db):
        db.xss_result.create_index([("task_id", 1)])
        db.sql_result.create_index([("task_id", 1)])

    with app.app_context():
        create_indexes(db)

    # GridFS setup
    app.fs = GridFS(app.db)

    # Inject helper classes
    app.sql_results = SQLResult(app.db)
    app.xss_results = XSSResult(app.db)

    # 🧠 Register Blueprints (do this last)
    from .views import views
    from .auth import auth
    from .test_routes import test_routes

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth)  # this is the one with /send-mfa
    app.register_blueprint(test_routes, url_prefix='/tests')

    socketio.init_app(app)
    from . import socket_events  # 👈 this auto-registers the handlers on startup

    print("App created, all blueprints registered")
    return app

