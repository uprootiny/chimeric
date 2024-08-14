from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import psutil
import uvicorn

app = FastAPI()

def get_system_metrics():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_io": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
        }
    }

@app.get("/metrics")
def metrics():
    metrics = get_system_metrics()
    return JSONResponse(content=metrics)

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    await websocket.accept()
    while True:
        metrics = get_system_metrics()
        await websocket.send_json(metrics)
        await asyncio.sleep(5)  # Send metrics every 5 seconds

if __name__ == "__main__":
    # Run the server with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7667)
