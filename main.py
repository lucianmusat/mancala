from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from player import HumanPlayer
from game import Game


app = FastAPI(
    title="Lucian's Mancala Game",
    description="A FastAPI implementation of the Mancala game",
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
    return populate_board(request)


@app.get("/select/")
def pit_selected(request: Request, user_id: int = Query(ge=0, le=1), pit: int = Query(ge=0, le=5)):
    if app.winner < 0:
        app.winner, app.turn = app.game.calculate_move(user_id, pit, app.turn)
    return populate_board(request)


@app.get("/reset")
def reset(request: Request):
    app.turn = 0
    app.winner = -1
    for player in app.players.values():
        player.reset()
    return populate_board(request)


@app.exception_handler(status.HTTP_404_NOT_FOUND)
@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
def http_exception_handler(request, _):
    return templates.TemplateResponse("404.html", {
        "request": request
    })
