use yew::prelude::*;
use log::Level;
use crate::common::types::GameData;

mod components;
mod stores;
mod common;

#[function_component(App)]
fn app() -> Html {
    let game_data = use_state(|| None::<GameData>);

    let update_game_data = {
        let game_data = game_data.clone();
        Callback::from(move |new_data: GameData| {
            game_data.set(Some(new_data));
        })
    };

    html! {
        <div id="container">
            <components::top_menu::TopMenu game_data={(*game_data).clone()} on_game_data_change={&update_game_data}/>
            <components::main_board::MainBoard game_data={(*game_data).clone()} on_game_data_change={&update_game_data} />
            <components::status::Status />
        </div>
    }
}

fn main() {
    console_log::init_with_level(Level::Debug).expect("error initializing log");
    yew::Renderer::<App>::new().render();
}