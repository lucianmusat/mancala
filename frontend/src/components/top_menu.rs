use yew::prelude::*;
use yew_router::prelude::*;
use web_sys::MouseEvent;
use crate::components::atoms::menu_button::MenuButton;
use crate::components::atoms::dropdown::Dropdown;
use log::error;
use yewdux::prelude::*;
use reqwasm::http::Request;
use crate::common::types::{BACKEND_URL};
use crate::Route;
use crate::stores::state_store::{StateStore, update_game_data, fetch_game_data};


#[function_component(TopMenu)]
pub fn top_menu() -> Html {
    let (store, dispatch) = use_store::<StateStore>();
    let navigator = use_navigator().unwrap();

    let home_callback = {
        let navigator = navigator.clone();
        Callback::from(move |e: MouseEvent| {
            e.prevent_default();
            navigator.push(&Route::Home);
        })
    };

    let about_callback = {
        let navigator = navigator.clone();
        Callback::from(move |e: MouseEvent| {
            e.prevent_default();
            navigator.push(&Route::About);
        })
    };

    let reset_callback = {
        let dispatch = dispatch.clone();
        let store = store.clone();
        Callback::from(move |e: MouseEvent| {
            e.prevent_default();
            let dispatch = dispatch.clone();
            let store = store.clone();
            if let Some(data) = &store.game_data {
                let url = format!("{}/reset?sessionid={}&difficulty={}", BACKEND_URL, data.session_id.clone(), data.difficulty.clone() as u8);
                let game_data = store.game_data.clone();
                wasm_bindgen_futures::spawn_local(async move {
                    match Request::get(&url).send().await {
                        Ok(_) => {
                            match fetch_game_data(Some(game_data.unwrap().session_id.clone())).await {
                                Ok(new_data) => update_game_data(&dispatch, new_data),
                                Err(err) => log::error!("Failed to fetch new game data: {}", err),
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

    let difficulty = store.game_data.as_ref().map(|data| data.difficulty.clone()).unwrap_or_default();

    html! {
        <div id="top-menu">
            <MenuButton text={"Home"} on_click={home_callback} />
            <MenuButton text={"Reset"} on_click={reset_callback} />
            <MenuButton text={"About"} on_click={about_callback} />
            <Dropdown difficulty={difficulty} />
        </div>
    }
}
