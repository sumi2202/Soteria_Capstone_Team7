from webapp import create_app
from flask import Flask, session

app = create_app()
app.secret_key = "SOFECapstone2425"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

if __name__ == '__main__':
    app.run(debug=True)