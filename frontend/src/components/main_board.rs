use std::string::ToString;
use yew::prelude::*;
use reqwasm::http::Request;
use anyhow::Error;
use serde::Deserialize;
use log::debug;
use std::collections::HashMap;

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
    let pebbles: HashMap<i32, &str> = [
        (0, ""),
        (1, "1stone.png"),
        (2, "2stones.png"),
        (3, "3stones.png"),
        (4, "4stones.png"),
        (5, "5stones.png"),
        (6, "6stones.png"),
    ].iter().cloned().collect();

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
        let board: Board = data.players[&0].board.clone();
        let p2_big_pit_class = if *winner == 1 { "big-pit-value blinking selected-pits" } else { "big-pit-value" };
        let p2_pits_class = if *turn == 1 && *winner < 0 { "selected-pits" } else { "" };
        let p1_pits_class = if *turn == 0 && *winner < 0 { "selected-pits" } else { "" };
        let p1_big_pit_class = if *winner == 0 { "big-pit-value blinking selected-pits" } else { "big-pit-value" };

        html! {
            <div id="main-board">
                <div id="p2-big-pit" class="p2-big-pit">
                    <div class={ p2_big_pit_class }>
                        { board.players_data[1].big_pit }
                    </div>
                    <div id="p2-pit-name">{"Player 2"}</div>
                </div>

                <div id="pits-container">
                    <div id="p2-pits" class={ p2_pits_class }>
                        { for board.players_data[1].pits.iter().rev().enumerate().map(|(index, pit)| {
                            let pit_index = board.players_data[1].pits.len() - index - 1;
                            let background_image = if *pit <= 6 {
                                                             format!("/{}", pebbles.get(pit).unwrap_or(&""))
                                                            } else {
                                                                "/multiple_stones.png".to_string()
                                                            };
                            let style = format!("background-image: url({}); background-repeat: no-repeat;", background_image);
                            let request_url = format!("/select?userid=1&pit={}&session={}", pit_index, data.session_id);
                            html! {
                                <>
                                    { if *turn == 1 && *pit > 0 && !*ai {
                                        html! { <a href={ request_url }></a> }
                                    } else { html! {} }}
                                    <div class="pit" style={ style }>
                                        { pit }
                                    </div>
                                </>
                            }
                        })}
                    </div>
                    <br />
                    <div id="p1-pits" class={ p1_pits_class }>
                        { for board.players_data[0].pits.iter().enumerate().map(|(index, pit)| {
                            let background_image = if *pit <= 6 {
                                                             format!("/{}", pebbles.get(pit).unwrap_or(&""))
                                                            } else {
                                                                "/multiple_stones.png".to_string()
                                                            };
                            let style = format!("background-image: url({}); background-repeat: no-repeat;", background_image);
                            let request_url = format!("/select?userid=1&pit={}&session={}", index, data.session_id);
                            html! {
                                <>
                                    { if *turn == 0 && *pit > 0 {
                                        html! { <a href={ request_url }></a> }
                                    } else { html! {} }}
                                    <div class="pit" style={ style} >
                                        { pit }
                                    </div>
                                </>
                            }
                        })}
                    </div>
                </div>

                <div id="p1-big-pit" class="p1-big-pit">
                    <div id="p1-pit-name">{"Player 1"}</div>
                    <div class={ p1_big_pit_class }>
                        { board.players_data[0].big_pit }
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
