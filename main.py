import logging

from fastapi import FastAPI, Request, status, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from datetime import timedelta
from uuid import uuid4
import redis
import pickle

from human_player import HumanPlayer
from random_player import RandomPlayer
from minimax_player import MiniMaxPlayer
from board import Board, NO_WINNER

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_EXPIRATION_HOURS = 72
STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    socket_connect_timeout=1,
    socket_timeout=1
)
assert redis.ping()

app = FastAPI(
    title="Lucian's Mancala Game",
    description="A basic implementation of the Mancala game",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://mancala.lucianmusat.nl",
        "https://mancala.lucianmusat.nl",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

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
    :return: The session state as a dictionary
    """
    session_state = redis.get(sessionid)
    if session_state:
        return pickle.loads(session_state)
    return {}


def default_session_state(sessionid: str, difficulty: str) -> dict:
    """
    Returns a default session state.
    """
    ret = {
        "session_id": sessionid,
        "difficulty": difficulty,
        "turn": "0",
        "winner": None,
        "board": app.board,
        "players": {
            0: app.players[0],
            1: app.players[1]
        }
    }
    return ret


def generate_response(sessionid: str) -> dict:
    session_state = get_session_state(sessionid)
    return {
        "session_id": sessionid,
        "difficulty": str(session_state['difficulty']),
        "turn": str(int(session_state['turn']) % 2),
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


@app.get("/api/")
def index(sessionid: str = Query(default="")):
    """
    Main index api call.
    :param sessionid: Session id to use in case of a continued game
    :return: The game's state
    """
    if not sessionid:
        print("Could not find previous session id, creating a new one")
        sessionid = str(uuid4())
        redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS),
                    pickle.dumps(default_session_state(sessionid, "0")))
    else:
        session_state = get_session_state(sessionid)
        app.board = session_state['board']
        app.players = session_state['players']
        app.winner = session_state['winner']
        app.turn = session_state['turn']
        app.difficulty = session_state['difficulty']

    response = {
        "session_id": sessionid,
        "difficulty": str(app.difficulty),
        "turn": "0",
        "winner": None,
        "players": {
            0: {
                "big_pit": app.board.players_data[0].big_pit,
                "pits": app.players[0].board.players_data[0].pits
            },
            1: {
                "big_pit": app.board.players_data[1].big_pit,
                "pits": app.players[1].board.players_data[1].pits
            }
        }
    }
    return response


@app.get("/api/select")
def pit_selected(userid: int = Query(ge=0, le=1),
                 pit: int = Query(ge=0, le=5),
                 sessionid: str = Query(default="")):
    """
    Api call upon selecting a pit to play from. Called
    by clicking in the pit in the GUI
    :param userid: Which user made the choice
    :param pit: Chosen pit index from the user's pit list
    :param sessionid: Session id to use
    :return: The new game's state
    """
    session_state = get_session_state(sessionid)
    assert len(session_state), "Session not found!"
    if not session_state['board'].game_over():
        if isinstance(session_state['players'][userid], HumanPlayer):
            session_state['players'][userid].select_pit(pit)
        if session_state['players'][userid].move():
            session_state['turn'] = int(session_state['turn']) + 1
    else:
        session_state['winner'] = session_state['board'].winner
    redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(session_state))
    response = generate_response(sessionid)
    return response


@app.get("/api/reset")
def reset(sessionid: str = Query(default=""), difficulty: int = Query(ge=0, le=1)):
    """
    Reset the game to it's initial state.
    :param sessionid: Session id to use
    :param difficulty: Difficulty level of the AI (0 easy, 1 hard)
    :return: New game's session state
    """
    app.board.reset()
    app.players = {
        0: HumanPlayer(0, app.board),
        # 1: RandomPlayer(1, app.board)
    }
    app.turn = 0
    app.winner = NO_WINNER
    app.difficulty = difficulty
    if difficulty == 0:
        app.players[1] = RandomPlayer(1, app.board)
    else:
        app.players[1] = MiniMaxPlayer(1, app.board)
    session_state = default_session_state(sessionid, str(difficulty))
    redis.setex(sessionid, timedelta(hours=REDIS_EXPIRATION_HOURS), pickle.dumps(session_state))
    return generate_response(sessionid)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(str(INDEX_HTML))

# SPA fallback: serve index.html for any non-API, non-static routes
@app.get("/{full_path:path}", include_in_schema=False)
def frontend_spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(str(INDEX_HTML))

@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def validation_handler(request: Request, exc):
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": exc.errors()})
