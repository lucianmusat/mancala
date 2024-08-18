use yew::prelude::*;
use log::Level;
use yew_router::{BrowserRouter, Routable, Switch};

mod components;
mod stores;
mod common;

#[derive(Clone, Routable, PartialEq)]
enum Route {
    #[at("/")]
    Home,
    #[at("/about")]
    About,
    #[at("/404")]
    NotFound,
}

fn switch(route: Route) -> Html {
    match route {
        Route::Home => html! { main_page() },
        Route::About => html! { about_page() },
        Route::NotFound => html! { not_found_page() },
    }
}

fn main_page() -> Html {
    html! {
        <div id="container">
            <components::top_menu::TopMenu/>
            <components::atoms::logo::Logo />
            <components::main_board::MainBoard />
            <components::status::Status />
        </div>
    }
}

fn about_page() -> Html {
    html! {
        <div id="container">
            <components::top_menu::TopMenu/>
            <components::atoms::logo::Logo />
            <components::about::About />
        </div>
    }
}

fn not_found_page() -> Html {
    html! {
        <div id="container">
            <components::top_menu::TopMenu/>
            <components::atoms::logo::Logo />
            <components::not_found::NotFound />
        </div>
    }
}

#[function_component(App)]
fn app() -> Html {
    html! {
        <BrowserRouter>
            <Switch<Route> render={switch} />
        </BrowserRouter>

    }
}

fn main() {
    console_log::init_with_level(Level::Debug).expect("error initializing log");
    yew::Renderer::<App>::new().render();
}
