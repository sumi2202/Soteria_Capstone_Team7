# webapp/socket_events.py
from flask_socketio import join_room
from webapp.extensions import socketio

@socketio.on("join")
def handle_join(data):
    email = data if isinstance(data, str) else data.get("email")
    if email:
        join_room(email)
        print(f"[SOCKET] ✅ User joined room: {email}")
