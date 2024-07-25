use yew::prelude::*;
use web_sys::MouseEvent;
use crate::components::atoms::menu_button::MenuButton;
use crate::components::atoms::dropdown::Dropdown;
use crate::components::atoms::dropdown::Difficulty;
use log::{info};

#[function_component(TopMenu)]
pub fn top_menu() -> Html {

    fn home_callback(e: MouseEvent) {
        e.prevent_default();
        info!("Home clicked");
    }

    fn reset_callback(e: MouseEvent) {
        e.prevent_default();
        info!("Reset clicked");
    }

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
