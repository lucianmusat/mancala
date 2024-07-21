use yew::prelude::*;
use wasm_bindgen::prelude::*;
use web_sys::MouseEvent;
use stylist::{yew::styled_component, Style};
use crate::components::atoms::menu_element::MenuElement;
use log::{debug, error, info};

#[derive(Debug, Clone, PartialEq)]
pub enum Difficulty {
    Easy,
    Hard,
}

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub difficulty: Difficulty,
}

#[styled_component(Dropdown)]
pub fn dropdown(props: &Props) -> Html {
    let is_dropdown_visible = use_state(|| false);

    let toggle_dropdown = {
        let is_dropdown_visible = is_dropdown_visible.clone();
        Callback::from(move |_| {
            let new_state = !*is_dropdown_visible;
            // debug!("Toggling dropdown, new state: {}", new_state);
            is_dropdown_visible.set(new_state);
        })
    };

    // These next two functions are used to hide the dropdown when the user clicks outside of it
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

    let style = Style::new(css!(
        r#"
            .top-dropdown {
                float: right;
                margin-right: 50px;
                margin-top: 25px;
                height: 100px;
                width: 200px;
                border-radius: 25px;
            }

            .dropdown-button {
                background-color: white;
                color: black;
                border: 2px solid lightgray;
                font-size: 24px;
                padding: 10px;
                cursor: pointer;
                border-radius: 10px;
                width: 120px;
                text-align: left;
            }

            .dropdown-button:hover {
                background-color: #f1f1f1;
            }

            .dropdown-menu {
                top: 100%;
                left: 0;
                padding: 0;
                margin: 0;
                background-color: white;
                border: 1px solid lightgray;
                border-top: none;
                border-radius: 0 0 4px 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                list-style: none;
                display: none;
            }
        "#
    ))
    .unwrap();

    fn easy_onclick(e: MouseEvent) {
        e.prevent_default();
        info!("Easy clicked");
    }

    fn hard_onclick(e: MouseEvent) {
        e.prevent_default();
        info!("Hard clicked");
    }

    html! {
        <div class="{style} top-dropdown">
            <button class="dropdown-button" onclick={toggle_dropdown}>{"Easy"} <span class="arrow down"></span></button>
            <ul class="dropdown-menu" style={dropdown_style}>
                <MenuElement text={"Easy"} on_click={easy_onclick} />
                <MenuElement text={"Hard"} on_click={hard_onclick} />
            </ul>
        </div>
    }
}