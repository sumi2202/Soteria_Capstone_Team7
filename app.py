from webapp import create_app
from flask import Flask, session
from flask_session import Session
from webapp.extensions import socketio

# Create Flask app
app = create_app()
app.secret_key = "SOFECapstone2425"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
Session(app)

# Run using SocketIO server
if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=5001, debug=True)
