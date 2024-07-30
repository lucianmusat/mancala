use std::time::Duration;
use yew::prelude::*;
use yew::{Html};
use reqwasm::http::Request;
use anyhow::Error;
use uuid::Uuid;
use log::{info, error, debug};
use stylist::{yew::styled_component, Style};
use yewdux::prelude::*;
use wasm_bindgen_futures::spawn_local;
use gloo_timers::future::sleep;
use crate::stores::state_store::{StateStore, update_game_data};
use crate::components::atoms::pit::{ClickData, Pit};
use crate::common::types::{BACKEND_URL, GameData, PlayerType};

#[styled_component(MainBoard)]
pub fn main_board() -> Html {
    let (store, dispatch) = use_store::<StateStore>();
    let fetched = use_state(|| false);

    {
        let fetched = fetched.clone();
        let dispatch = dispatch.clone();
        use_effect(move || {
            if !*fetched {
                spawn_local(async move {
                    match fetch_game_data().await {
                        Ok(data) => {
                            update_game_data(&dispatch, data.clone());
                            info!("Game data fetched successfully: {}", data.session_id);
                        },
                        Err(err) => error!("Failed to fetch game data: {}", err),
                    }
                });
                fetched.set(true);
            }
            || ()
        });
    }

    {
        let store = store.clone();
        let dispatch = dispatch.clone();
        use_effect(move || {
            if let Some(game_data) = &store.game_data {
                let player_one_disabled = game_data.turn != PlayerType::Player1;
                let session_id = game_data.session_id;
                if player_one_disabled {
                    let dispatch = dispatch.clone();
                    spawn_local(async move {
                        sleep(Duration::from_secs(1)).await;
                        // Make AI move
                        match fetch_move(session_id, PlayerType::Player2, 0).await {
                            Ok(data) => update_game_data(&dispatch, data),
                            Err(err) => error!("Failed to fetch AI move: {}", err),
                        }
                    });
                }
            }
            || ()
        });
    }

    if store.game_data.is_none() {
        return html! {
            <div>{"Loading..."}</div>
        };
    }

    info!("Game data: {:?}", store.game_data.as_ref().unwrap());

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

    let session_id = store.game_data.as_ref().unwrap().session_id;

    let on_pit_clicked = {
        let dispatch = dispatch.clone();
        Callback::from(move |data: ClickData| {
            let dispatch = dispatch.clone();
            info!("Pit clicked: {}", data.id);
            wasm_bindgen_futures::spawn_local(async move {
                match fetch_move(session_id, data.player_type, data.id).await {
                    Ok(data) => update_game_data(&dispatch, data),
                    Err(_) => error!("Failed to fetch move"),
                }
            });
        })
    };

    let player_one_pits = store.game_data.as_ref().unwrap().players.get(&0).unwrap().pits.clone();
    let player_two_pits = store.game_data.as_ref().unwrap().players.get(&1).unwrap().pits.clone();
    let current_turn = &store.game_data.as_ref().unwrap().turn;
    let player_one_disabled = *current_turn != PlayerType::Player1;
    let player_two_disabled = *current_turn != PlayerType::Player2;

    html! {
        <div id="main-board" class={style}>
            <table>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_two_pits.get(i).map_or(0, |&v| v)} player_type={PlayerType::Player2}
                                id={i as u32} on_click={on_pit_clicked.clone()} disabled={player_two_disabled} /></td>
                    }) }
                </tr>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_one_pits.get(5 - i).map_or(0, |&v| v)} player_type={PlayerType::Player1}
                                id={(5 - i) as u32} on_click={on_pit_clicked.clone()} disabled={player_one_disabled} /></td>
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
    let url = format!("{}/select?userid={}&session={}&pit={}", BACKEND_URL, player_type as u32, session_id, pit_id);
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
