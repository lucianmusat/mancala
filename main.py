from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from player import HumanPlayer
from game import Game


app = FastAPI(
    title="Lucian's Mancala Game",
    description="A very basic FastAPI implementation of the Mancala game",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.players = {
    0: HumanPlayer(),
    1: HumanPlayer()
}
app.game = Game(app.players)
app.turn = 0
app.winner = -1


def populate_board(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {
        "request": request,
        "players": app.players,
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
def pit_selected(request: Request, user_id: int = Query(ge=0, le=1), pit: int = Query(ge=0, le=5)):
    """
    Api call to select one pit to play from.
    Called upon clicking one of the player's pits from the web interface.
    :param request: Current request context
    :param user_id: Which user made the choice
    :param pit: Chosen pit index from the user's pit list
    :return: TemplateResponse that will render the board with the new data
    """
    if app.winner < 0:
        app.winner, app.turn = app.game.calculate_move(user_id, pit, app.turn)
    return populate_board(request)


@app.get("/reset")
def reset(request: Request):
    """
    Reset the game to it's initial state.
    :param request: Current request context
    :return: TemplateResponse that will render the freshly reset board
    """
    app.turn = 0
    app.winner = -1
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
