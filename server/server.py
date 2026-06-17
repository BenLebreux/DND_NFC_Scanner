import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Mount the static files directory
app.mount("/public", StaticFiles(directory="public"), name="public")

# In-memory database of NFC UIDs to Enemy stats
db: Dict[str, Any] = {
    "04:62:5C:82:1E:61:80": {"name": "Sample Goblin", "hp": 10, "maxHp": 15, "conditions": []}
}

current_enemy = None  # The enemy currently being displayed on the CYD

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send current display state to newly connected client
        if current_enemy:
            await websocket.send_json({"event": "update_display", "data": current_enemy["data"]})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

class EntityData(BaseModel):
    name: str
    hp: int
    maxHp: int
    conditions: List[str]

class EntityUpdate(BaseModel):
    uid: str
    data: EntityData

class ScanRequest(BaseModel):
    uid: str

class DebugLog(BaseModel):
    log: str

@app.get("/")
async def read_index():
    return FileResponse("public/index.html")

@app.get("/api/entities")
async def get_entities():
    return db

@app.post("/api/entities")
async def update_entity(req: EntityUpdate):
    global current_enemy
    db[req.uid] = req.data.dict()
    
    # If this entity is currently displayed, broadcast the update
    if current_enemy and current_enemy["uid"] == req.uid:
        current_enemy["data"] = db[req.uid]
        await manager.broadcast({"event": "update_display", "data": current_enemy["data"]})
        
    return {"success": True, "db": db}

@app.post("/api/scan")
async def handle_scan(req: ScanRequest):
    global current_enemy
    uid = req.uid
    print(f"[SCAN] Received NFC UID: {uid}")
    await manager.broadcast({"event": "server_log", "data": {"message": f"NFC Tag Scanned: {uid}", "uid": uid}})

    if uid in db:
        print(f"[SCAN] Found matching entity: {db[uid]['name']}")
        current_enemy = {"uid": uid, "data": db[uid]}
        await manager.broadcast({"event": "update_display", "data": current_enemy["data"]})
    else:
        print(f"[SCAN] Unknown UID. Broadcasting generic prompt.")
        current_enemy = {"uid": uid, "data": {"name": "Unknown Tag", "hp": 0, "maxHp": 0, "conditions": []}}
        await manager.broadcast({"event": "update_display", "data": current_enemy["data"]})
        await manager.broadcast({"event": "unknown_tag_scanned", "data": {"uid": uid}})
        
    return {"success": True}

@app.post("/api/debug")
async def handle_debug(req: DebugLog):
    await manager.broadcast({"event": "debug_log", "data": {"log": req.log}})
    return {"success": True}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect the CYD or dashboard to send us anything over WS,
            # but we need to receive to keep the connection alive and detect disconnects.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("A client disconnected")

if __name__ == "__main__":
    import uvicorn
    # Run the server on all interfaces so the CYD can connect
    uvicorn.run("server:app", host="0.0.0.0", port=3000, reload=False)
