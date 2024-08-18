use std::time::Duration;
use yew::prelude::*;
use yew::{Html};
use reqwasm::http::Request;
use anyhow::Error;
use uuid::Uuid;
use log::{error, debug};
use stylist::{yew::styled_component, Style};
use yewdux::prelude::*;
use wasm_bindgen_futures::spawn_local;
use gloo_timers::future::sleep;
use crate::stores::state_store::{StateStore, update_game_data, fetch_game_data};
use crate::components::atoms::pit::{ClickData, Pit};
use crate::components::atoms::big_pit::BigPit;
use crate::common::types::{BACKEND_URL, GameData, PlayerType};

#[derive(Properties, PartialEq, Clone)]
pub struct Props {
    pub keep_session: bool,
}

#[styled_component(MainBoard)]
pub fn main_board(props: &Props) -> Html {
    let (store, dispatch) = use_store::<StateStore>();
    let fetched = use_state(|| false);

    {
        let fetched = fetched.clone();
        let dispatch = dispatch.clone();
        let keep_session  = props.keep_session;
        use_effect(move || {
            if !*fetched && !keep_session {
                spawn_local(async move {
                    match fetch_game_data(None).await {
                        Ok(data) => {
                            update_game_data(&dispatch, data.clone());
                            debug!("Game data fetched successfully: {}", data.session_id);
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
        let force_update = use_state(|| 0);
        use_effect(move || {
            if let Some(game_data) = &store.game_data {
                let session_id = game_data.session_id;
                if game_data.turn == PlayerType::Player2 {
                    let dispatch = dispatch.clone();
                    let force_update = force_update.clone();
                    spawn_local(async move {
                        sleep(Duration::from_secs(1)).await;
                        // Make AI move
                        match fetch_move(session_id, PlayerType::Player2, 0).await {
                            Ok(data) => update_game_data(&dispatch, data),
                            Err(err) => error!("Failed to fetch AI move: {}", err),
                        }
                        // Update the state to force re-run of effect
                        force_update.set(*force_update + 1);
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

    debug!("Game data: {:?}", store.game_data.as_ref().unwrap());

    let style = Style::new(css!(
        r#"
            .big_board_table {
                border-collapse: collapse;
                width: 745px;
                margin-top: 40px;
                margin-right: 5px;
                height: 340px;
            }
            td {
                padding: 10px;
                text-align: center;
            }
            .left-margin {
                width: 46px;
            }
            .left-margin-pits {
                width: 20px;
            }
        "#
    )).unwrap();

    let session_id = store.game_data.as_ref().unwrap().session_id;

    let on_pit_clicked = {
        let dispatch = dispatch.clone();
        Callback::from(move |data: ClickData| {
            let dispatch = dispatch.clone();
            debug!("Pit clicked: {}", data.id);
            spawn_local(async move {
                match fetch_move(session_id, data.player_type, data.id).await {
                    Ok(data) => update_game_data(&dispatch, data),
                    Err(_) => error!("Failed to fetch move"),
                }
            });
        })
    };

    let player_one_pits = store.game_data.as_ref().unwrap().players.get(&0).unwrap().pits.clone();
    let player_one_big_pit = store.game_data.as_ref().unwrap().players.get(&0).unwrap().big_pit;
    let player_two_pits = store.game_data.as_ref().unwrap().players.get(&1).unwrap().pits.clone();
    let player_two_big_pit = store.game_data.as_ref().unwrap().players.get(&1).unwrap().big_pit;
    let current_turn = &store.game_data.as_ref().unwrap().turn;
    let player_one_disabled = *current_turn != PlayerType::Player1;
    let player_two_disabled = *current_turn != PlayerType::Player2;

    html! {
       <div class={style} id="center-wrapper">
            <div id="main-board">
                <div class="left-margin"/>
                <BigPit value={player_two_big_pit} player_type={PlayerType::Player2} reversed=false />
                <div class="left-margin-pits"/>
                <table class="big_board_table">
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
                <BigPit value={player_one_big_pit} player_type={PlayerType::Player1} reversed=true/>
            </div>
        </div>
    }
}

async fn fetch_move(session_id: Uuid, player_type: PlayerType,  pit_id: u32) -> Result<GameData, Error> {
    debug!("Fetching move...");
    let url = format!("{}/select?userid={}&sessionid={}&pit={}", BACKEND_URL, player_type as u32, session_id, pit_id);
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
