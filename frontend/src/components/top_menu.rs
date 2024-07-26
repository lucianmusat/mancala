use anyhow::Error;
use yew::prelude::*;
use web_sys::MouseEvent;
use crate::components::atoms::menu_button::MenuButton;
use crate::components::atoms::dropdown::Dropdown;
use log::{debug, info};
use reqwasm::http::Request;
use crate::common::types::{BACKEND_URL, Difficulty};

#[function_component(TopMenu)]
pub fn top_menu() -> Html {

    fn home_callback(e: MouseEvent) {
        e.prevent_default();
        info!("Home clicked");
    }

    let reset_callback = |e: MouseEvent| {
        e.prevent_default();
        info!("Reset clicked");
        // let url = format!("{}/reset?session={}&difficulty={}", BACKEND_URL, session_id, difficulty);
        // let response = Request::get(&url)
        //     .send()
        //     .await
        //     .map_err(|err| anyhow::anyhow!("Request failed: {}", err));
    };

    fn about_callback(e: MouseEvent) {
        e.prevent_default();
        info!("About clicked");
    }

    html! {
        <div id="top-menu">
            <MenuButton text={"Home"} on_click={home_callback} />
            <MenuButton text={"Reset"} on_click={reset_callback} />
            <MenuButton text={"About"} on_click={about_callback} />
            <Dropdown difficulty={Difficulty::Easy} />
        </div>
    }
}
