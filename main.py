from move import HumanMove
from player import Player
from board import Board

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

board = Board()
human_move_strategy = HumanMove(board)
player1 = Player(1, human_move_strategy)
player2 = Player(2, human_move_strategy)


app = FastAPI(
    title="Lucian's Mancala Game",
    description="A FastAPI implementation of the Mancala game",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def populate_board(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {
        "request": request,
        "p1_big_pit_value": player1.big_pit,
        "p2_big_pit_value": player2.big_pit,
        "p1_1": player1.pits[0],
        "p1_2": player1.pits[1],
        "p1_3": player1.pits[2],
        "p1_4": player1.pits[3],
        "p1_5": player1.pits[4],
        "p1_6": player1.pits[5],
        "p2_1": player2.pits[0],
        "p2_2": player2.pits[1],
        "p2_3": player2.pits[2],
        "p2_4": player2.pits[3],
        "p2_5": player2.pits[4],
        "p2_6": player2.pits[5]
    })


@app.get("/", status_code=200)
def index(request: Request):
    return populate_board(request)


@app.get("/select/user/{user_id}/pit/{pit}", status_code=200)
def pit_selected(request: Request, user_id: int, pit: int):
    player = player1 if user_id == 1 else player2
    player.move(pit)
    return populate_board(request)


@app.get("/reset", status_code=200)
def reset(request: Request):
    board.reset_board()
    return populate_board(request)
