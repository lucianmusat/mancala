use yew::prelude::*;
use web_sys::MouseEvent;
use crate::components::atoms::menu_button::MenuButton;
use crate::components::atoms::dropdown::Dropdown;
use log::{info, error};
use anyhow::Error;
use reqwasm::http::Request;
use wasm_bindgen_futures::spawn_local;
use crate::common::types::{BACKEND_URL, GameData};

#[derive(Properties, PartialEq)]
pub struct Props {
    pub game_data: Option<GameData>,
    pub on_game_data_change: Callback<GameData>
}

#[function_component(TopMenu)]
pub fn top_menu(props: &Props) -> Html {

    fn home_callback(e: MouseEvent) {
        e.prevent_default();
        info!("Home clicked");
    }

    fn about_callback(e: MouseEvent) {
        e.prevent_default();
        info!("About clicked");
    }

    let reset_callback = {
        let game_data = props.game_data.clone();
        let on_game_data_change = props.on_game_data_change.clone();
        Callback::from(move |e: MouseEvent| {
            e.prevent_default();
            if let Some(data) = &game_data {
                info!("Reset clicked");
                let url = format!("{}/reset?session={}&difficulty={}", BACKEND_URL, data.session_id, data.difficulty.clone() as u8);
                let on_game_data_change = on_game_data_change.clone();
                spawn_local(async move {
                    match Request::get(&url).send().await {
                        Ok(_) => {
                            info!("Reset successful");
                            match fetch_game_data().await {
                                Ok(new_data) => {
                                    info!("New game data fetched");
                                    on_game_data_change.emit(new_data);
                                },
                                Err(err) => error!("Failed to fetch new game data: {}", err),
                            }
                        },
                        Err(err) => error!("Reset failed: {}", err),
                    }
                });
            } else {
                error!("Cannot reset: game data not available");
            }
        })
    };

    let difficulty = props.game_data.as_ref().map(|data| data.difficulty.clone()).unwrap_or_default();

    html! {
        <div id="top-menu">
            <MenuButton text={"Home"} on_click={home_callback} />
            <MenuButton text={"Reset"} on_click={reset_callback} />
            <MenuButton text={"About"} on_click={about_callback} />
            <Dropdown difficulty={difficulty} />
        </div>
    }
}

async fn fetch_game_data() -> Result<GameData, Error> {
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