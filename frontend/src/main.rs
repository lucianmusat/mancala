use yew::prelude::*;
use log::Level;

mod components;
mod stores;
mod common;

#[function_component(App)]
fn app() -> Html {
    html! {
        <div id="container">
            <components::top_menu::TopMenu/>
            <components::atoms::logo::Logo />
            <components::main_board::MainBoard />
            <components::status::Status />
        </div>
    }
}

fn main() {
    console_log::init_with_level(Level::Debug).expect("error initializing log");
    yew::Renderer::<App>::new().render();
}