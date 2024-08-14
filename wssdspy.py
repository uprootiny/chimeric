import asyncio
import json
import logging
import os
import time

import aiohttp
import websockets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the port from environment variables, defaulting to 3333
PORT = int(os.getenv("PORT", 3333))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def generate_ollama_response(prompt: str, model: str = "llama3", websocket=None):
    """Sends a prompt to the Ollama API and streams the generated response."""
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.post(url, json=data) as response:
                response.raise_for_status()  # Raise an exception for bad status codes
                end_time = time.time()
                latency = int((end_time - start_time) * 1000)

                async for chunk in response.content.iter_chunked(1024):
                    chunk_data = json.loads(chunk.decode("utf-8"))
                    chunk_data["latency"] = latency
                    timestamp = time.strftime("%H:%M:%S", time.localtime())
                    response_data = {
                        "text": chunk_data["response"],
                        "timestamp": timestamp,
                        "latency": chunk_data["latency"],
                        "type": "bot"
                    }
                    await websocket.send(json.dumps(response_data))

    except aiohttp.ClientError as e:
        logging.error(f"Error communicating with Ollama API: {e}")
        error_response = {
            "text": f"Error: {e}",
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "latency": None,
            "type": "error"
        }
        await websocket.send(json.dumps(error_response))

async def handle_connection(websocket: websockets.WebSocketServerProtocol, path: str):
    """Handles incoming WebSocket connections and processes messages."""
    logging.info(f"New client connected from {websocket.remote_address}")

    async for message in websocket:
        logging.info(f"Received message from client: {message}")
        await generate_ollama_response(message, websocket=websocket)

async def main():
    """Starts the WebSocket server and runs the main event loop."""
    async with websockets.serve(handle_connection, "localhost", PORT):
        logging.info(f"WebSocket server started on ws://localhost:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())