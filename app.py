from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import threading
import websockets
import os

app = Flask(__name__)

# CORS for frontend domain
CORS(app, resources={
    r"/*": {
        "origins": ["https://chat-implement.netlify.app", "http://localhost:5173"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

connected = set()

async def chat_handler(web_socket):
    connected.add(web_socket)
    try:
        async for message in web_socket:
            await web_socket.send(f"You: {message}")
            for connection in connected:
                if connection != web_socket:
                    await connection.send(f"Other: {message}")
    finally:
        connected.remove(web_socket)

def run_websocket_server():
    async def server():
        port = int(os.environ.get("PORT", 5000))
        host = "0.0.0.0"
        async with websockets.serve(chat_handler, host, port, ping_interval=None):
            print(f"WebSocket server running on ws://{host}:{port}")
            await asyncio.Future()

    asyncio.run(server())

# Start WebSocket server in a background thread
threading.Thread(target=run_websocket_server, daemon=True).start()

@app.route("/")
def home():
    return jsonify({"message": "Flask with WebSocket is running!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
