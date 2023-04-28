from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from human_player import HumanPlayer
# from random_player import RandomPlayer
from minimax_player import MiniMaxPlayer
from board import Board, NO_WINNER

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

app.board = Board(nr_players=2)
app.players = {
    0: HumanPlayer(0, app.board),
    1: MiniMaxPlayer(1, app.board)
}
app.turn = 0
app.winner = NO_WINNER


def populate_board(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {
        "request": request,
        "board": app.board,
        "pebbles": app.pebbles,
        "turn": app.turn % 2,
        "winner": app.winner,
        "ai": not all(isinstance(player, HumanPlayer) for player in app.players.values())
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
def pit_selected(request: Request, userid: int = Query(ge=0, le=1), pit: int = Query(ge=0, le=5)):
    """
    Api call upon selecting a pit to play from. Called
    by clicking on the pit in the GUI
    :param request: Current request context
    :param userid: Which user made the choice
    :param pit: Chosen pit index from the user's pit list
    :return: TemplateResponse that will render the board with the new data
    """
    if app.winner < 0:
        if isinstance(app.players[userid], HumanPlayer):
            app.players[userid].select_pit(pit)

        if app.players[userid].move():
            app.turn += 1
        app.winner = app.board.winner
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
    app.board.reset()
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
