import sys
from threading import Thread
from app import app  # Import your existing Flask app
from cefpython3 import cefpython as cef

# Function to start Flask in a separate thread
def start_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

# Function to start the CEF browser window
def start_cef():
    cef.Initialize()
    window_info = cef.WindowInfo()
    window_info.windowless = True  # This is needed to display the webview
    cef.CreateBrowserSync(url="http://127.0.0.1:5000", window_info=window_info, window_title="Soteria App")
    cef.MessageLoop()
    cef.Shutdown()

if __name__ == "__main__":
    # Run Flask server in a separate thread
    Thread(target=start_flask, daemon=True).start()

    # Start the CEF browser
    start_cef()
