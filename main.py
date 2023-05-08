import logging

from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datetime import timedelta
from uuid import uuid4
import redis
import pickle

from human_player import HumanPlayer
from random_player import RandomPlayer
from minimax_player import MiniMaxPlayer
from board import Board, NO_WINNER

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_EXPIRATION_HOURS = 72

redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT)
assert redis.ping()

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
app.difficulty = 0


def get_session_state(session_id: str) -> dict:
    """
    Get the session state from redis.
    :param session_id: The session id
    """
    session_state = redis.get(session_id)
    if session_state:
        return pickle.loads(session_state)
    return {}


def default_session_state() -> dict:
    """
    Returns a default session state.
    """
    return {"board": app.board,
            "turn": app.turn,
            "winner": app.winner,
            "players": app.players,
            "difficulty": 0,
            }


def populate_board(request: Request, session_id: str) -> templates.TemplateResponse:
    """
    Populates the board with the current session state.
    :param request: The current request context
    :param session_id: The session id for which the board is populated
    :return: TemplateResponse that will render the board
    """
    session_state = get_session_state(session_id)
    if not session_state:
        return templates.TemplateResponse("404.html", {
            "request": request
        })
    return templates.TemplateResponse("new_index.html", {
        "request": request,
        "board": session_state['board'],
        "pebbles": app.pebbles,
        "turn": session_state['turn'] % 2,
        "winner": session_state['winner'],
        "ai": not all(isinstance(player, HumanPlayer) for player in session_state['players'].values()),
        "session_id": session_id,
        "difficulty": session_state['difficulty'],
    })


@app.get("/")
def index(request: Request):
    """
    Main index Api call. Generates a new session id.
    :param request: Current request context
    :return: TemplateResponse that will render the landing page
    """
    session_id = str(uuid4())
    redis.setex(session_id, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(default_session_state()))
    return populate_board(request, session_id)


@app.get("/select/")
def pit_selected(request: Request,
                 userid: int = Query(ge=0, le=1),
                 pit: int = Query(ge=0, le=5),
                 session: str = Query(default="")):
    """
    Api call upon selecting a pit to play from. Called
    by clicking on the pit in the GUI
    :param request: Current request context
    :param userid: Which user made the choice
    :param pit: Chosen pit index from the user's pit list
    :param session: Session id to use
    :param difficulty: Difficulty level of the AI (0 easy, 1 hard)
    :return: TemplateResponse that will render the board with the new data
    """
    session_state = get_session_state(session)
    assert len(session_state), "Session not found!"
    if session_state['winner'] < 0:
        if isinstance(session_state['players'][userid], HumanPlayer):
            session_state['players'][userid].select_pit(pit)
        if session_state['players'][userid].move():
            session_state['turn'] += 1
        session_state['winner'] = session_state['board'].winner
    redis.setex(session, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(session_state))
    return populate_board(request, session)


@app.get("/reset")
def reset(request: Request, session: str = Query(default=""), difficulty: int = Query(ge=0, le=1)):
    """
    Reset the game to it's initial state.
    :param request: Current request context
    :param session: Session id to use
    :param difficulty: Difficulty level of the AI (0 easy, 1 hard)
    :return: TemplateResponse that will render the freshly reset board
    """
    new_session = default_session_state()
    new_session['difficulty'] = difficulty
    if difficulty == 0:
        logging.debug("Using AI easy")
        print("Using AI easy")
        new_session['players'][1] = RandomPlayer(1, new_session['board'])
    else:
        logging.debug("Using AI hard")
        print("Using AI hard")
        new_session['players'][1] = MiniMaxPlayer(1, new_session['board'])
    redis.setex(session, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(new_session))
    return populate_board(request, session)


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
