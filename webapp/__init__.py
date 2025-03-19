from flask import Flask
from pymongo import MongoClient
from gridfs import GridFS
from .models import SQLResult, XSSResult

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhfbdbfjksd hfjksdkjdh'
    app.secret_key = 'SOFECapstone2425'

    # MongoDB Setup
    app.config['MONGO_URI'] = 'mongodb+srv://SoteriaUser:SOFEcapstone2425@soteriacluster.g7txq.mongodb.net/'
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database('soteria')

    # Initialize GridFS
    app.fs = GridFS(app.db)

    # Create indexes for MongoDB collections within app context
    def create_indexes(db):
        """Create indexes for the required fields in MongoDB collections."""
        db.xss_result.create_index([("task_id", 1)])  # Ascending index
        db.sql_result.create_index([("task_id", 1)])  # Ascending index

    # Run the index creation inside the app context
    with app.app_context():
        create_indexes(app.db)

    # Initialize the models
    app.sql_results = SQLResult(app.db)
    app.xss_results = XSSResult(app.db)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .test_routes import test_routes

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth)
    app.register_blueprint(test_routes, url_prefix='/run_tests')

    return app
