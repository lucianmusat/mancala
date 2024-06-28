use yew::prelude::*;

#[function_component(Status)]
pub fn status() -> Html {
    html! {
        <div id="status">
            <p class="neonText">{"Player X wins!"}</p>
        </div>
    }
}
