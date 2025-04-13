from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import threading
import websockets

app = Flask(__name__)
CORS(app)

connected = set()

def run_websocket_server(port):
    async def chat_handler(web_socket):
        connected.add(web_socket)
        try:
            async for message in web_socket:
                for connection in connected:
                    if connection != web_socket:
                        await connection.send(message)
        finally:
            connected.remove(web_socket)

    async def server():
        async with websockets.serve(chat_handler, "localhost", port):
            await asyncio.Future()

    asyncio.run(server())

@app.route("/give_port/<int:port>", methods=["GET"])
def give_port(port):
    try:
        thread = threading.Thread(target=run_websocket_server, args=(port,))
        thread.daemon = True
        thread.start()
        return jsonify({ "message": "successful" })
    except Exception as e:
        print("Error:", e)
        return jsonify({ "message": "unsuccessful" })

if __name__ == "__main__":
    app.run(debug=True)
