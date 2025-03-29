import threading
import webview
from webapp import create_app
from flask import Flask, session
from flask_session import Session

# Create Flask app
app = create_app()
app.secret_key = "SOFECapstone2425"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
Session(app)

# Function to run Flask in a separate thread
def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Flask in a background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Create the window without specifying the GUI
    webview.create_window("Soteria", "http://127.0.0.1:5000")
    webview.start()
