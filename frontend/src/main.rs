use yew::prelude::*;
mod components;

#[function_component(App)]
fn app() -> Html {
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
