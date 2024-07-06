use yew::prelude::*;
mod components;
use log::{Level};

#[function_component(App)]
fn app() -> Html {
    console_log::init_with_level(Level::Debug).expect("error initializing log");
    html! {
        <div id="container">
            <components::top_menu::TopMenu />
            <components::main_board::MainBoard />
            <components::status::Status />
        </div>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}
