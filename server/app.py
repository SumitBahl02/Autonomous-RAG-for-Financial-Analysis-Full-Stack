from flask import Flask, render_template
from flask_socketio import SocketIO, disconnect, send
from flask_cors import CORS
from services.Architecture import get_response
# Create a Flask app
flaskapp = Flask(__name__)
CORS(flaskapp)

# Configure the Socket.IO server
socketio = SocketIO(flaskapp, cors_allowed_origins="*")

# Define a route for the home page
@flaskapp.route("/")
def index():
    return "Hello, Flask-SocketIO!"

@socketio.on("connect")
def test_connect():
    print("Client connected")
    # send("Hello from Flask-SocketIO!")

@socketio.on("chat")
def start_chat(data):
    print("Chat Started", data)
    query= data.get("query")
    print("Query", query, "\n now starting chat")
    # socketio.emit("chat", "Chat Started")
    # socketio.emit("update", "Chat Started")
    # send("Chat Started")
    get_response(query,socketio)
    socketio.emit("end-stream", {"End of Stream":"End of Stream"})
    disconnect()

def emitter(event_name, value):
    print("Emitting", event_name, value)
    socketio.emit(event_name, value)

import random
import string
import time

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# join mei AI message.content, thought
@socketio.on("simulate-chat")
def simulate_chat(data):
    print("Simulating Chat Started", data)
    query = data.get("query", "default query")
    print("Query:", query)
    data = [
    {
        "username": "Supervisor",
        "isAgent": True,
        "parentAgent": "Query",
        "content": "Hello, how can I help you today?",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "Finance",
        "isAgent": True,
        "parentAgent": "Supervisor",
        "content": "Try checking the server configurations.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "Budget Advisor",
        "isAgent": False,
        "parentAgent": "Finance",
        "content": "Yes, James is right. Let's check that as well.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "Stock analysor",
        "isAgent": False,
        "parentAgent": "Finance",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "Math",
        "isAgent": True,
        "parentAgent": "Supervisor",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "calculator",
        "isAgent": False,
        "parentAgent": "Math",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "statistics",
        "isAgent": False,
        "parentAgent": "Math",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "Research",
        "isAgent": True,
        "parentAgent": "Supervisor",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "pdf",
        "isAgent": False,
        "parentAgent": "Research",
        "content": "I think there might be an issue with our CDN configuration.",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    {
        "username": "News Updator",
        "isAgent": False,
        "parentAgent": "Research",
        "content": "Deployment error fixed. Good job, team!",
        "thought": "I am here to help you with your queries.",
        "isUser": False,
        "verdict": "passing to next agent",
    },
    ]

    for obj in data:
        socketio.emit("update", obj)
        time.sleep(10 / 30)

    print("Simulation complete!")
    socketio.emit("end-stream", {"End of Stream":"End of Stream"})
    disconnect()
    

# Run the app
if __name__ == "__main__":
    socketio.run(flaskapp, host="0.0.0.0", port=5000)
