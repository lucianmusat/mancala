from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from board import Board
from move import HumanMove
from player import Player
from utils import MoveResult

board = Board()
human_move_strategy = HumanMove(board)
player1 = Player(1, human_move_strategy)
player2 = Player(2, human_move_strategy)
turn = 0
winner = 0


def check_win() -> int:
    assert player1.big_pit + player2.big_pit + sum(player1.pits) + sum(player2.pits) == 72, \
        f"There was a problem in the stone moves!"
    if all(stones == 0 for stones in player1.pits):
        player2.collect_all_stones()
        return 1 if player1.big_pit > player2.big_pit else 2
    if all(stones == 0 for stones in player2.pits):
        player1.collect_all_stones()
        return 1 if player1.big_pit > player2.big_pit else 2
    return 0


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
        "p2_6": player2.pits[5],
        "turn": turn % 2,
        "winner": winner
    })


@app.get("/")
def index(request: Request):
    return populate_board(request)


@app.get("/select/")
def pit_selected(user_id: int, pit: int, request: Request):
    global turn, winner
    if not winner:
        player = player1 if user_id == 1 else player2
        if (turn % 2 == 0 and player.id == 1) or (turn % 2 == 1 and player.id == 2):
            if player.move(pit) == MoveResult.Valid:
                turn += 1
                winner = check_win()
    return populate_board(request)


@app.get("/reset")
def reset(request: Request):
    global turn, winner
    winner = 0
    turn = 0
    board.reset_board()
    return populate_board(request)
