use yew::prelude::*;

#[function_component(TopMenu)]
pub fn top_menu() -> Html {
    html! {
        <div id="top-menu">
            <a href="/"><div class="top-button">{"Home"}</div></a>
            <a href="/reset"><div class="top-button">{"Reset"}</div></a>
            <a href="/about"><div class="top-button">{"About"}</div></a>
            <div class="top-dropdown">
                <button class="dropdown-button">{"Easy"}</button>
                <ul class="dropdown-menu">
                    <li><a href="#">{"Easy"}</a></li>
                    <li><a href="#">{"Hard"}</a></li>
                </ul>
            </div>
        </div>
    }
}
