use yew::prelude::*;
use yew::{Html, Properties};
use reqwasm::http::Request;
use anyhow::Error;
use serde::Deserialize;
use uuid::Uuid;
use log::{info, error, debug};
use std::collections::HashMap;
use stylist::{yew::styled_component, Style};

use crate::components::atoms::pit::{ClickData, Pit};


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
    session_id: Uuid,
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

pub enum Msg {
    PitClicked(u32),
}

#[styled_component(MainBoard)]
pub fn main_board() -> Html {

    let game_data = use_state(|| None::<GameData>);
    let fetched = use_state(|| false);
    let _ai = use_state(|| false);

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

    // Not sure if this is the best way, but for now let's leave it
    if game_data.clone().is_none() {
        return html! {
            <div>{"Loading..."}</div>
        };
    }

    info!("Game data: {:?}", game_data.clone().as_ref().unwrap());

    let style = Style::new(css!(
        r#"
            table {
                border-collapse: collapse;
                width: 770px;
                margin-left: 140px;
                margin-top: 35px;
                height: 350px;
            }
            td {
                padding: 10px;
                text-align: center;

            }
        "#
    )).unwrap();

    let session_id = game_data.clone().as_ref().unwrap().session_id;

    let on_pit_clicked = {
        let session_id = session_id.clone();
        let game_data = game_data.clone();
        Callback::from(move |data: ClickData| {
            info!("Pit clicked: {}", data.id);
            let session_id = session_id.clone();
            let game_data = game_data.clone();
            wasm_bindgen_futures::spawn_local(async move {
                match fetch_move(session_id, data.player_type, data.id).await {
                    Ok(data) => game_data.set(Some(data)),
                    Err(_) => error!("Failed to fetch move"),
                }
            });
        })
    };

    let player_one_pits = &game_data.clone().as_ref().unwrap().players.get(&0).unwrap().board.players_data[0].pits.clone();
    let player_two_pits = &game_data.clone().as_ref().unwrap().players.get(&1).unwrap().board.players_data[1].pits.clone();

    html! {
        <div id="main-board" class={style}>
            <table>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_two_pits.get(i).map_or(0, |&v| v as u32)} player_type={PlayerType::Player2} id={i as u32} on_click={on_pit_clicked.clone()} /></td>
                    }) }
                </tr>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_one_pits.get(5 - i).map_or(0, |&v| v as u32)} player_type={PlayerType::Player1} id={(5 - i) as u32} on_click={on_pit_clicked.clone()} /></td>
                    }) }
                </tr>
            </table>
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

async fn fetch_move(session_id: Uuid, player_type: PlayerType,  pit_id: u32) -> Result<GameData, Error> {
    debug!("Fetching move...");
    let url = format!("{}/select?userid={}&session={}&pit={}", BACKEND_URL, player_type_to_int(player_type), session_id, pit_id);
    let response = Request::get(&url)
        .send()
        .await
        .map_err(|err| anyhow::anyhow!("Request failed: {}", err))?;

    let data = response
        .json::<GameData>()
        .await
        .map_err(|err| anyhow::anyhow!("Failed to parse JSON: {}", err))?;

    Ok(data)
}

fn player_type_to_int(player_type: PlayerType) -> i32 {
    match player_type {
        PlayerType::Player1 => 0,
        PlayerType::Player2 => 1,
    }
}