import asyncio
import websockets
import json
import aiohttp

# Ollama API Endpoint and Model
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

async def query_ollama(prompt):
    """Send a prompt to the Ollama API and return the response."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False  # Set to True if you want to handle streaming responses
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("response", "No response received")
            else:
                return f"Ollama API error: {response.status}"

async def handle_connection(websocket, path):
    async for message in websocket:
        try:
            # Parse the incoming message
            plan_piece = message
            print(f"Received plan piece: {plan_piece}")

            # Send the plan piece to Ollama and get the response
            ollama_response = await query_ollama(plan_piece)

            # Send the result back to the client
            await websocket.send(f"Ollama Response: {ollama_response}")
        except Exception as e:
            print(f"Error processing message: {e}")
            await websocket.send(f"Error: {str(e)}")

start_server = websockets.serve(handle_connection, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
