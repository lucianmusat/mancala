use yew::prelude::*;

#[function_component(Status)]
pub fn status() -> Html {
    let is_visible = use_state(|| false);
    let style = if *is_visible {
        "display: block;"
    } else {
        "display: none;"
    };

    html! {
        <div id="status" style={ style }>
            <p class="neonText">{"Player X wins!"}</p>
        </div>
    }
}
