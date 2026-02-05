import logging
import os
import pickle
from pathlib import Path
from uuid import uuid4

from cachetools import TTLCache

from fastapi import FastAPI, Request, status, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from human_player import HumanPlayer
from random_player import RandomPlayer
from minimax_player import MiniMaxPlayer
from board import Board, NO_WINNER

# In-process session store (single replica app)
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "72"))
SESSION_CACHE_MAXSIZE = int(os.getenv("SESSION_CACHE_MAXSIZE", "10000"))

_session_cache = TTLCache(maxsize=SESSION_CACHE_MAXSIZE, ttl=SESSION_TTL_HOURS * 3600)

STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

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
    1: RandomPlayer(1, app.board),
}
app.turn = 0
app.winner = NO_WINNER
app.difficulty = 0


def get_session_state(sessionid: str) -> dict:
    """Get the session state from an in-memory TTL cache."""
    payload = _session_cache.get(sessionid)
    if payload is None:
        return {}
    return pickle.loads(payload)


def set_session_state(sessionid: str, session_state: dict) -> None:
    """Persist session state to an in-memory TTL cache."""
    _session_cache[sessionid] = pickle.dumps(session_state)


def default_session_state(sessionid: str, difficulty: str) -> dict:
    """Returns a default session state."""
    return {
        "session_id": sessionid,
        "difficulty": difficulty,
        "turn": "0",
        "winner": None,
        "board": app.board,
        "players": {0: app.players[0], 1: app.players[1]},
    }


def generate_response(sessionid: str) -> dict:
    session_state = get_session_state(sessionid)
    return {
        "session_id": sessionid,
        "difficulty": str(session_state["difficulty"]),
        "turn": str(int(session_state["turn"]) % 2),
        "winner": str(session_state["winner"]) if session_state["winner"] is not None else None,
        "players": {
            0: {
                "big_pit": session_state["board"].players_data[0].big_pit,
                "pits": session_state["board"].players_data[0].pits,
            },
            1: {
                "big_pit": session_state["board"].players_data[1].big_pit,
                "pits": session_state["board"].players_data[1].pits,
            },
        },
    }


@app.get("/api/")
def index(sessionid: str = Query(default="")):
    """Main index api call."""
    if not sessionid:
        logging.info("No session id provided; creating a new one")
        sessionid = str(uuid4())
        set_session_state(sessionid, default_session_state(sessionid, "0"))
        return {
            "session_id": sessionid,
            "difficulty": str(app.difficulty),
            "turn": "0",
            "winner": None,
            "players": {
                0: {
                    "big_pit": app.board.players_data[0].big_pit,
                    "pits": app.players[0].board.players_data[0].pits,
                },
                1: {
                    "big_pit": app.board.players_data[1].big_pit,
                    "pits": app.players[1].board.players_data[1].pits,
                },
            },
        }

    session_state = get_session_state(sessionid)
    if not session_state:
        # Session expired / not found: create a new one and return it.
        logging.info("Session %s not found/expired; creating a new one", sessionid)
        sessionid = str(uuid4())
        set_session_state(sessionid, default_session_state(sessionid, "0"))
        return {
            "session_id": sessionid,
            "difficulty": str(app.difficulty),
            "turn": "0",
            "winner": None,
            "players": {
                0: {
                    "big_pit": app.board.players_data[0].big_pit,
                    "pits": app.players[0].board.players_data[0].pits,
                },
                1: {
                    "big_pit": app.board.players_data[1].big_pit,
                    "pits": app.players[1].board.players_data[1].pits,
                },
            },
        }

    app.board = session_state["board"]
    app.players = session_state["players"]
    app.winner = session_state["winner"]
    app.turn = session_state["turn"]
    app.difficulty = session_state["difficulty"]

    return {
        "session_id": sessionid,
        "difficulty": str(app.difficulty),
        "turn": "0",
        "winner": None,
        "players": {
            0: {
                "big_pit": app.board.players_data[0].big_pit,
                "pits": app.players[0].board.players_data[0].pits,
            },
            1: {
                "big_pit": app.board.players_data[1].big_pit,
                "pits": app.players[1].board.players_data[1].pits,
            },
        },
    }


@app.get("/api/select")
def pit_selected(
    userid: int = Query(ge=0, le=1),
    pit: int = Query(ge=0, le=5),
    sessionid: str = Query(default=""),
):
    """Api call upon selecting a pit to play from."""
    session_state = get_session_state(sessionid)
    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session_state["board"].game_over():
        if isinstance(session_state["players"][userid], HumanPlayer):
            session_state["players"][userid].select_pit(pit)
        if session_state["players"][userid].move():
            session_state["turn"] = int(session_state["turn"]) + 1
    else:
        session_state["winner"] = session_state["board"].winner

    set_session_state(sessionid, session_state)
    return generate_response(sessionid)


@app.get("/api/reset")
def reset(sessionid: str = Query(default=""), difficulty: int = Query(ge=0, le=1)):
    """Reset the game to it's initial state."""
    if not sessionid:
        sessionid = str(uuid4())

    app.board.reset()
    app.players = {
        0: HumanPlayer(0, app.board),
    }
    app.turn = 0
    app.winner = NO_WINNER
    app.difficulty = difficulty

    if difficulty == 0:
        app.players[1] = RandomPlayer(1, app.board)
    else:
        app.players[1] = MiniMaxPlayer(1, app.board)

    session_state = default_session_state(sessionid, str(difficulty))
    set_session_state(sessionid, session_state)
    return generate_response(sessionid)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(str(INDEX_HTML))


# SPA fallback: serve index.html for any non-API, non-static routes
@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str):
    if path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")
    if path.startswith("static"):
        raise HTTPException(status_code=404, detail="Not found")
    if "." in path.split("/")[-1]:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse("static/index.html")


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def validation_handler(request: Request, exc):
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": exc.errors()})
