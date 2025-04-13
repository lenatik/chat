from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import threading
import websockets
import os

app = Flask(__name__)

# Configure CORS for deployment
CORS(app, resources={
    r"/*": {
        "origins": ["https://chat-implement.netlify.app", "https://your-deployed-server.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

connected = set()

def run_websocket_server(port):
    async def chat_handler(web_socket):
        connected.add(web_socket)
        try:
            async for message in web_socket:
                # Send message back to sender and broadcast to others
                await web_socket.send(f"You: {message}")  # Echo back
                for connection in connected:
                    if connection != web_socket:
                        await connection.send(f"Other: {message}")  # Broadcast
        finally:
            connected.remove(web_socket)

    async def server():
        host = "0.0.0.0" if os.environ.get("DEPLOYED") else "localhost"
        async with websockets.serve(chat_handler, host, port):
            await asyncio.Future()

    asyncio.run(server())

@app.route("/give_port/<int:port>", methods=["GET"])
def give_port(port):
    try:
        thread = threading.Thread(target=run_websocket_server, args=(port,))
        thread.daemon = True
        thread.start()
        return jsonify({"message": "successful"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "unsuccessful"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)  # Use '0.0.0.0' to bind to all IPs for cloud hosting
