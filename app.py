from webapp import create_app
from flask import Flask, session
from flask_session import Session

app = create_app()
app.secret_key = "SOFECapstone2425"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
Session(app)

if __name__ == '__main__':
    app.run(debug=True)