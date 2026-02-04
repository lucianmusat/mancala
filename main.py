import logging

from fastapi import FastAPI, Request, status, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from uuid import uuid4
import os
import pickle

from cassandra.cluster import Cluster

from human_player import HumanPlayer
from random_player import RandomPlayer
from minimax_player import MiniMaxPlayer
from board import Board, NO_WINNER

# Cassandra config
CASSANDRA_CONTACT_POINTS = os.getenv("CASSANDRA_CONTACT_POINTS", "cassandra").split(",")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "mancala")
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "72"))

STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

_cluster = Cluster(CASSANDRA_CONTACT_POINTS, port=CASSANDRA_PORT)
_cassandra = _cluster.connect()

# Ensure schema exists (safe for a small app; idempotent)
_cassandra.execute(
    f"""
    CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
    """
)
_cassandra.set_keyspace(CASSANDRA_KEYSPACE)
_cassandra.execute(
    """
    CREATE TABLE IF NOT EXISTS game_sessions (
      session_id text PRIMARY KEY,
      state blob,
      updated_at timestamp
    );
    """
)

_stmt_get = _cassandra.prepare("SELECT state FROM game_sessions WHERE session_id=?")
_stmt_set = _cassandra.prepare(
    "INSERT INTO game_sessions (session_id, state, updated_at) VALUES (?, ?, toTimestamp(now())) USING TTL ?"
)


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
    """Get the session state from Cassandra."""
    row = _cassandra.execute(_stmt_get, (sessionid,)).one()
    if row and row.state:
        return pickle.loads(row.state)
    return {}


def set_session_state(sessionid: str, session_state: dict) -> None:
    """Persist session state to Cassandra with a TTL."""
    ttl_seconds = SESSION_TTL_HOURS * 3600
    payload = pickle.dumps(session_state)
    _cassandra.execute(_stmt_set, (sessionid, payload, ttl_seconds))


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
        logging.info("Could not find previous session id, creating a new one")
        sessionid = str(uuid4())
        set_session_state(sessionid, default_session_state(sessionid, "0"))
    else:
        session_state = get_session_state(sessionid)
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
    assert len(session_state), "Session not found!"

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
