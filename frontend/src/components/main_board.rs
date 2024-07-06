use std::string::ToString;
use yew::prelude::*;
use serde_json::from_str;
use reqwasm::http::Request;
use anyhow::Error;
use serde::Deserialize;
use log::debug;

const BACKEND_URL: &str = "http://localhost:8000";

#[derive(Deserialize, Debug, Clone)]
struct PlayerData {
    big_pit: i32,
    pits: Vec<i32>,
}

#[derive(Deserialize, Debug, Clone)]
struct Board {
    nr_players: i32,
    players_data: Vec<PlayerData>,
}

#[derive(Deserialize, Debug, Clone)]
struct Player {
    selected_pit: Option<i32>,
    index: i32,
    board: Board,
}

#[derive(Deserialize, Debug, Clone)]
struct GameData {
    session_id: String,
    difficulty: i32,
    turn: i32,
    winner: i32,
    players: std::collections::HashMap<i32, Player>,
}

#[function_component(MainBoard)]
pub fn main_board() -> Html {
    let game_data = use_state(|| None::<GameData>);
    let fetched = use_state(|| false);
    {
        let game_data = game_data.clone();
        use_effect(move || {
            if !*fetched {
                wasm_bindgen_futures::spawn_local(async move {
                    match fetch_game_data().await {
                        Ok(data) => game_data.set(Some(data)),
                        Err(_) => log::error!("Failed to fetch game data"),
                    }
                });
                fetched.set(true);
            }
            || ()
        });
    }

    if let Some(data) = (*game_data).clone() {
        let nr_players = data.players[&0].board.nr_players;
        let players: Vec<Player> = data.players.values().cloned().collect();

        html! {
            <div id="main-board">
                <div id="pits-container">
                    <div id="p1-pits">
                        { format!("Number of players: {}", nr_players) }
                        // TODO: Render other parts of the board based on `players`
                    </div>
                </div>
            </div>
        }
    } else {
        html! { <div>{"Loading..."}</div> }
    }
}

async fn fetch_game_data() -> Result<GameData, Error> {
    debug!("Fetching game data!");
    let response = Request::get(BACKEND_URL)
        .send()
        .await
        .map_err(|err| anyhow::anyhow!("Request failed: {}", err))?;

    let data = response
        .json::<GameData>()
        .await
        .map_err(|err| anyhow::anyhow!("Failed to parse JSON: {}", err))?;

    Ok(data)
}
