use yew::prelude::*;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::MouseEvent;
// use log::debug;

#[function_component(TopMenu)]
pub fn top_menu() -> Html {
    let is_dropdown_visible = use_state(|| false);

    let toggle_dropdown = {
        let is_dropdown_visible = is_dropdown_visible.clone();
        Callback::from(move |_| {
            let new_state = !*is_dropdown_visible;
            // debug!("Toggling dropdown, new state: {}", new_state);
            is_dropdown_visible.set(new_state);
        })
    };

    let hide_dropdown = {
        let is_dropdown_visible = is_dropdown_visible.clone();
        Callback::from(move |e: MouseEvent| {
            let target = e.target().unwrap().dyn_into::<web_sys::Element>().unwrap();
            let is_click_inside = target.closest(".top-dropdown").unwrap().is_some();
            // debug!("Click detected. Is click inside dropdown: {}", is_click_inside);
            if !is_click_inside {
                is_dropdown_visible.set(false);
            }
        })
    };

    use_effect_with(is_dropdown_visible.clone(), move |_| {
        let hide_dropdown_clone = hide_dropdown.clone();
        let window = web_sys::window().unwrap();
        let document = window.document().unwrap();
        let body = document.body().unwrap();
        let closure = Closure::wrap(Box::new(move |e: web_sys::Event| {
            hide_dropdown_clone.emit(e.dyn_into::<MouseEvent>().unwrap());
        }) as Box<dyn FnMut(_)>);

        body.add_event_listener_with_callback("click", closure.as_ref().unchecked_ref()).unwrap();
        closure.forget();

        || {}
    });

    let dropdown_style = if *is_dropdown_visible {
        "display: block;"
    } else {
        "display: none;"
    };

    html! {
        <div id="top-menu">
            <a href="/"><div class="top-button">{"Home"}</div></a>
            <a href="/reset"><div class="top-button">{"Reset"}</div></a>
            <a href="/about"><div class="top-button">{"About"}</div></a>
            <div class="top-dropdown">
                <button class="dropdown-button" onclick={toggle_dropdown}>{"Easy"} <span class="arrow down"></span></button>
                <ul class="dropdown-menu" style={dropdown_style}>
                    <li><a href="#">{"Easy"}</a></li>
                    <li><a href="#">{"Hard"}</a></li>
                </ul>
            </div>
        </div>
    }
}
