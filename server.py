from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")
class Game:
    def __init__(self):
        self.players = []
        self.board = [""] * 9
        self.current_player = None

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        self.current_player = self.players[0]

    def toggle_player(self):
        self.current_player = self.players[1] if self.current_player == self.players[0] else self.players[0]

    async def broadcast_state(self):
        for player in self.players:
            await player.send_text(self.get_game_state())

    def get_game_state(self):
        return {"board": self.board, "current_player": self.players.index(self.current_player) + 1}


game = Game()


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    await websocket.accept()
    game.add_player(websocket)
    if len(game.players) == 2:
        game.start_game()
        await game.broadcast_state()

    try:
        while True:
            data = await websocket.receive_text()
            # Handle game logic here
            if data.startswith("move"):
                move_index = int(data.split(" ")[1])
                if game.current_player == websocket and 0 <= move_index < 9 and game.board[move_index] == "":
                    game.board[move_index] = "X" if game.current_player == game.players[0] else "O"
                    game.toggle_player()
                    await game.broadcast_state()
            # You can add more game logic here

    except Exception as e:
        print(e)
    finally:
        game.players.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: dict):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
