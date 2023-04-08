import time

from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from human_player import HumanPlayer
from random_player import RandomPlayer
from player import NO_WINNER
from game import Game


app = FastAPI(
    title="Lucian's Mancala Game",
    description="A basic implementation of the Mancala game",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.pebbles = {
    0: "",
    1: "1stone.png",
    2: "2stones.png",
    3: "3stones.png",
    4: "4stones.png",
    5: "5stones.png",
    6: "6stones.png"
}

app.players = {
    0: HumanPlayer(),
    1: RandomPlayer()
}
app.game = Game(app.players)
app.turn = 0
app.winner = NO_WINNER


def populate_board(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {
        "request": request,
        "players": app.players,
        "pebbles": app.pebbles,
        "turn": app.turn % 2,
        "winner": app.winner
    })


@app.get("/")
def index(request: Request):
    """
    Main index Api call.
    :param request: Current request context
    :return: TemplateResponse that will render the landing page
    """
    return populate_board(request)


@app.get("/select/")
def pit_selected(request: Request, pit: int = Query(ge=0, le=5)):
    """
    Api call upon selecting a pit to play from. Can be called
    by clicking on the pit in the GUI, or by the AI player.
    :param request: Current request context
    :param pit: Chosen pit index from the user's pit list
    :return: TemplateResponse that will render the board with the new data
    """
    # Render the board after every calculate_move and don't block the request
    if app.winner < 0:
        app.winner, app.turn = app.game.calculate_move(0, pit, app.turn)
        # AI player's turn
        while app.turn != 0 and app.winner < 0:
            time.sleep(1)
            app.winner, app.turn = app.game.calculate_move(1, 0, app.turn)
    return populate_board(request)


@app.get("/reset")
def reset(request: Request):
    """
    Reset the game to it's initial state.
    :param request: Current request context
    :return: TemplateResponse that will render the freshly reset board
    """
    app.turn = 0
    app.winner = NO_WINNER
    for player in app.players.values():
        player.reset()
    return populate_board(request)


@app.exception_handler(status.HTTP_404_NOT_FOUND)
@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
def http_exception_handler(request, _):
    """
    Handle other missing api calls by rendering
    a friendly 404 page.
    :param request: Current request context
    :param _:
    :return: TemplateResponse that will render the 404 page
    """
    return templates.TemplateResponse("404.html", {
        "request": request
    })
