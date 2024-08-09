import logging
import uuid

from fastapi import FastAPI, Request, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.board = Board(nr_players=2)
app.players = {
    0: HumanPlayer(0, app.board),
    1: RandomPlayer(1, app.board)
}
app.turn = 0
app.winner = NO_WINNER
app.difficulty = 0


def get_session_state(sessionid: str) -> dict:
    """
    Get the session state from redis.
    :param sessionid: The session id
    """
    session_state = redis.get(sessionid)
    if session_state:
        print(f"Found session state: {pickle.loads(session_state)} for id {sessionid}")
        return pickle.loads(session_state)
    return {}


def default_session_state(sessionid: str) -> dict:
    """
    Returns a default session state.
    """
    ret = {
        "session_id": sessionid,
        "difficulty": "0",
        "turn": "0",
        "winner": None,
        "board": app.board,
        "players": {
            0: app.players[0],
            1: app.players[1]
        }
    }
    print(f"Setting default session state: {ret}")
    return ret


def generate_response(sessionid: str) -> dict:
    session_state = get_session_state(sessionid)
    return {
        "session_id": sessionid,
        "difficulty": str(session_state['difficulty']),
        "turn": str(session_state['turn'] % 2),
        "winner": str(session_state['winner']) if session_state['winner'] is not None else None,
        "players": {
            0: {
                "big_pit": session_state['board'].players_data[0].big_pit,
                "pits": session_state['board'].players_data[0].pits
            },
            1: {
                "big_pit": session_state['board'].players_data[1].big_pit,
                "pits": session_state['board'].players_data[1].pits
            }
        }
    }


@app.get("/")
def index(sessionid: str = Query(default="")):
    """
    Main index Api call. Generates a new session id.
    :param sessionid: Session id to use in case of a continued game
    :return: TemplateResponse that will render the landing page
    """
    if sessionid:
        print("No need to reset")
    else:
        sessionid = str(uuid4())
        redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(default_session_state(sessionid)))
    response = {
        "session_id": sessionid,
        "difficulty": "0",
        "turn": "0",
        "winner": None,
        "players": {
            0: {
                "big_pit": app.players[0].board.players_data[0].big_pit,
                "pits": app.players[0].board.players_data[0].pits
            },
            1: {
                "big_pit": app.players[1].board.players_data[1].big_pit,
                "pits": app.players[1].board.players_data[1].pits
            }
        }
    }
    print(f"Response: {response}")
    return response


@app.get("/select/")
def pit_selected(userid: int = Query(ge=0, le=1),
                 pit: int = Query(ge=0, le=5),
                 sessionid: str = Query(default="")):
    """
    Api call upon selecting a pit to play from. Called
    by clicking in the pit in the GUI
    :param userid: Which user made the choice
    :param pit: Chosen pit index from the user's pit list
    :param sessionid: Session id to use
    :return: TemplateResponse that will render the board with the new data
    """
    session_state = get_session_state(sessionid)
    print(f"Session state: {session_state}")
    assert len(session_state), "Session not found!"
    if session_state['winner'] is None:
        if isinstance(session_state['players'][userid], HumanPlayer):
            session_state['players'][userid].select_pit(pit)
        if session_state['players'][userid].move():
            session_state['turn'] = int(session_state['turn']) + 1
        session_state['winner'] = session_state['winner']
    redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(session_state))
    response = generate_response(sessionid)
    print(f"Response: {response}")
    return response


@app.get("/reset")
def reset(sessionid: str = Query(default=""), difficulty: int = Query(ge=0, le=1)):
    """
    Reset the game to it's initial state.
    :param sessionid: Session id to use
    :param difficulty: Difficulty level of the AI (0 easy, 1 hard)
    :return: TemplateResponse that will render the freshly reset board
    """
    session_state = get_session_state(sessionid)
    session_state['difficulty'] = difficulty
    if difficulty == 0:
        print("Using AI easy")
        session_state['players'][1] = RandomPlayer(1, app.players[1].board)
    else:
        print("Using AI hard")
        session_state['players'][1] = MiniMaxPlayer(1, app.players[1].board)
    app.players[1].board.reset()
    app.players[0].board.reset()
    app.board.reset()
    session_state['turn'] = 0
    session_state['board'].reset()
    redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(session_state))
    print(f"Set to redis {session_state}")
    print(f"Generated response: {generate_response(sessionid)}")
    return generate_response(sessionid)


# @app.get("/about")
# def index(request: Request, session: str = Query(default="")):
#     """
#     About page Api call.
#     :return: TemplateResponse that will render the about page
#     """
#     return templates.TemplateResponse("about.html", {"request": request, "session_id": session})


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
    return 404
