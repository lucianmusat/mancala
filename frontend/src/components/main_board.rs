use yew::prelude::*;
use yew::{Html, Properties};
use reqwasm::http::Request;
use anyhow::Error;
use uuid::Uuid;
use log::{info, error, debug};
use stylist::{yew::styled_component, Style};

use crate::components::atoms::pit::{ClickData, Pit};
use crate::common::types::{BACKEND_URL, GameData, PlayerType};


#[derive(Properties, PartialEq)]
pub struct Props {
    pub game_data: Option<GameData>,
    pub on_game_data_change: Callback<GameData>,
}

#[styled_component(MainBoard)]
pub fn main_board(props: &Props) -> Html {

    let fetched = use_state(|| false);
    let _ai = use_state(|| false);

    {
        let on_game_data_change = props.on_game_data_change.clone();
        use_effect(move || {
            if !*fetched {
                wasm_bindgen_futures::spawn_local(async move {
                    match fetch_game_data().await {
                        Ok(data) =>  on_game_data_change.emit(data),
                        Err(err) => error!("Failed to fetch game data: {}", err),
                    }
                });
                fetched.set(true);
            }
            || ()
        });
    }

    // Not sure if this is the best way, but for now let's leave it
    if props.game_data.is_none() {
        return html! {
            <div>{"Loading..."}</div>
        };
    }

    info!("Game data: {:?}", &props.game_data.as_ref().unwrap());

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

    let session_id = props.game_data.as_ref().unwrap().session_id;

    let on_pit_clicked = {
        let on_game_data_change = props.on_game_data_change.clone();
        Callback::from(move |data: ClickData| {
            info!("Pit clicked: {}", data.id);
            let on_game_data_change = on_game_data_change.clone();
            wasm_bindgen_futures::spawn_local(async move {
                match fetch_move(session_id, data.player_type, data.id).await {
                    Ok(data) => on_game_data_change.emit(data),
                    Err(_) => error!("Failed to fetch move"),
                }
            });
        })
    };

    let player_one_pits = props.game_data.as_ref().unwrap().players.get(&0).unwrap().pits.clone();
    let player_two_pits = props.game_data.as_ref().unwrap().players.get(&1).unwrap().pits.clone();

    html! {
        <div id="main-board" class={style}>
            <table>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_two_pits.get(i).map_or(0, |&v| v)} player_type={PlayerType::Player2} id={i as u32} on_click={on_pit_clicked.clone()} /></td>
                    }) }
                </tr>
                <tr>
                    { for (0..6).rev().map(|i| html! {
                        <td><Pit value={player_one_pits.get(5 - i).map_or(0, |&v| v)} player_type={PlayerType::Player1} id={(5 - i) as u32} on_click={on_pit_clicked.clone()} /></td>
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
