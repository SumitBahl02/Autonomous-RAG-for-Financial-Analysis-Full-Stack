from .app import app, socketio
from flask_socketio import send
from app.services.Architecture import supervisor
from flask import jsonify
@app.route("/")
def index():
    return jsonify("Hello, Flask-SocketIO!")

# Define a Socket.IO event
@socketio.on("connect")
def test_connect():
    print("Client connected")
    # send("Hello from Flask-SocketIO!")

@socketio.on("chat")
def start_chat(data):
    print("Chat Started", data)
    query= data.get("query")
    print("Query", query)
    # supervisor.stream(query)
    send("Chat Started")


