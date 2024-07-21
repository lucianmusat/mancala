use yew::prelude::*;
use yew::{Html, Properties};
use wasm_bindgen::prelude::*;
use reqwasm::http::Request;
use anyhow::Error;
use serde::Deserialize;
use log::{info, error, debug};
use std::collections::HashMap;
use crate::components::atoms::pit::Pit;


const BACKEND_URL: &str = "http://localhost:8000";

#[derive(Debug, Clone)]
pub enum PlayerType {
    Player1,
    Player2,
}

impl PartialEq for PlayerType {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (PlayerType::Player1, PlayerType::Player1) => true,
            (PlayerType::Player2, PlayerType::Player2) => true,
            _ => false,
        }
    }
}

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
    players: HashMap<i32, Player>,
}

#[derive(Properties, Clone, PartialEq)]
pub struct PitProps {
    pub index: usize,
    pub value: usize,
    pub session_id: String,
}


#[function_component(MainBoard)]
pub fn main_board() -> Html {



    let turn = use_state(|| 0);
    let winner = use_state(|| -1);
    let game_data = use_state(|| None::<GameData>);
    let fetched = use_state(|| false);
    let ai = use_state(|| false);

    {
        let game_data = game_data.clone();
        use_effect(move || {
            if !*fetched {
                wasm_bindgen_futures::spawn_local(async move {
                    match fetch_game_data().await {
                        Ok(data) => game_data.set(Some(data)),
                        Err(_) => error!("Failed to fetch game data"),
                    }
                });
                fetched.set(true);
            }
            || ()
        });
    }

    info!("Game data: {:?}", game_data);

    if let Some(data) = (*game_data).clone() {
        let nr_players = data.players[&0].board.nr_players;
        let players: Vec<Player> = data.players.values().cloned().collect();
        let board: Board = data.players[&0].board.clone();
        let p2_big_pit_class = if *winner == 1 { "big-pit-value blinking selected-pits" } else { "big-pit-value" };
        let p2_pits_class = if *turn == 1 && *winner < 0 { "selected-pits" } else { "" };
        let p1_pits_class = if *turn == 0 && *winner < 0 { "selected-pits" } else { "" };
        let p1_big_pit_class = if *winner == 0 { "big-pit-value blinking selected-pits" } else { "big-pit-value" };
    }

    html! {
        <div id="main-board">
            <Pit value=6 player_type={PlayerType::Player1} id=0 on_click={Callback::noop()} />
        </div>
    }
}

async fn fetch_game_data() -> Result<GameData, Error> {
    debug!("Fetching game data...");
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
