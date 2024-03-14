from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}?chatId=<chat_id>`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int,List[WebSocket]] = {}

    async def connect(self,chatId, websocket: WebSocket):
        await websocket.accept()
        # self.active_connections.append(websocket)
        if chatId not in self.active_connections:
            # If not, create an empty list for that chat_id
            self.active_connections[chatId] = []
        self.active_connections[chatId].append(websocket)

    def disconnect(self,chatId, websocket: WebSocket):
        # self.active_connections.remove(websocket)
        self.active_connections.pop(chatId)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self,chatId, message: str):
        for connections in self.active_connections[chatId]:
            await connections.send_text(message)

manager = ConnectionManager()

@app.get("/{chatId}")
async def get(chatId):
    print(html)
    return HTMLResponse(html.replace("<chat_id>", chatId))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int,chatId:int):
    await manager.connect(chatId,websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(chatId,f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(chatId,websocket)
        await manager.broadcast(chatId,f"Client #{client_id} left the chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
