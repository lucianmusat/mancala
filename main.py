import logging
import os
import pickle
from pathlib import Path
from uuid import uuid4

from cachetools import TTLCache

from fastapi import FastAPI, Request, status, Query, HTTPException
from pydantic import BaseModel
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
    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")

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


def _create_new_session(difficulty: str = "0") -> dict:
    """Create a new session and return the initial game state payload."""
    sessionid = str(uuid4())
    set_session_state(sessionid, default_session_state(sessionid, difficulty))
    return generate_response(sessionid)


@app.post("/api/sessions", status_code=status.HTTP_201_CREATED)
def create_session():
    """Create a new session.

    Frontend should call this when no session id exists locally or when an existing
    session id returns 404 (expired / not found).
    """
    logging.info("Creating a new session")
    return _create_new_session("0")


@app.get("/api/sessions/{sessionid}")
def get_session(sessionid: str):
    """Fetch an existing session state."""
    return generate_response(sessionid)


# Backwards-compatible endpoint: historically both fetched or implicitly created.
@app.get("/api/")
def index(sessionid: str = Query(default="")):
    """Main index api call (legacy).

    If sessionid is missing or expired, a new session is created.
    """
    if not sessionid:
        logging.info("No session id provided; creating a new one (legacy /api/)")
        return _create_new_session("0")

    session_state = get_session_state(sessionid)
    if not session_state:
        logging.info("Session %s not found/expired; creating a new one (legacy /api/)", sessionid)
        return _create_new_session("0")

    # Ensure generate_response sees it.
    return generate_response(sessionid)


class SelectMoveRequest(BaseModel):
    userid: int
    pit: int


class ResetRequest(BaseModel):
    difficulty: int


def _apply_move(sessionid: str, userid: int, pit: int) -> dict:
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


def _reset_session(sessionid: str, difficulty: int) -> dict:
    # Ensure the session exists (resetting a missing session should be explicit).
    if not get_session_state(sessionid):
        raise HTTPException(status_code=404, detail="Session not found")

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


@app.post("/api/sessions/{sessionid}/select")
def session_select(sessionid: str, payload: SelectMoveRequest):
    """Make a move within a session."""
    # Extra safety: enforce expected ranges here too.
    if payload.userid not in (0, 1):
        raise HTTPException(status_code=422, detail="userid must be 0 or 1")
    if payload.pit < 0 or payload.pit > 5:
        raise HTTPException(status_code=422, detail="pit must be between 0 and 5")
    return _apply_move(sessionid, payload.userid, payload.pit)


@app.post("/api/sessions/{sessionid}/reset")
def session_reset(sessionid: str, payload: ResetRequest):
    """Reset an existing session."""
    if payload.difficulty not in (0, 1):
        raise HTTPException(status_code=422, detail="difficulty must be 0 or 1")
    return _reset_session(sessionid, payload.difficulty)


# Legacy endpoints (querystring-based)
@app.get("/api/select")
def pit_selected(
    userid: int = Query(ge=0, le=1),
    pit: int = Query(ge=0, le=5),
    sessionid: str = Query(default=""),
):
    """Legacy: Api call upon selecting a pit to play from."""
    return _apply_move(sessionid, userid, pit)


@app.get("/api/reset")
def reset(sessionid: str = Query(default=""), difficulty: int = Query(ge=0, le=1)):
    """Legacy: Reset the game to it's initial state.

    Historically this created a new session if no sessionid was provided.
    """
    if not sessionid:
        sessionid = str(uuid4())
        set_session_state(sessionid, default_session_state(sessionid, str(difficulty)))
        return generate_response(sessionid)

    # If the session exists, reset it; otherwise keep old behavior of creating a new one.
    if not get_session_state(sessionid):
        set_session_state(sessionid, default_session_state(sessionid, str(difficulty)))
        return generate_response(sessionid)

    return _reset_session(sessionid, difficulty)


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
