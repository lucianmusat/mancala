use yew::prelude::*;
use wasm_bindgen::prelude::*;
use web_sys::MouseEvent;
use stylist::{yew::styled_component, Style};
use crate::components::atoms::menu_element::MenuElement;
use crate::common::types::{BACKEND_URL, Difficulty};
use log::{debug, info, error};
use yewdux::use_store;
use reqwasm::http::Request;
use wasm_bindgen_futures::spawn_local;
use crate::stores::state_store::{fetch_game_data, StateStore, update_game_data};

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub difficulty: Difficulty,
}

#[styled_component(Dropdown)]
pub fn dropdown(_props: &Props) -> Html {
    let is_dropdown_visible = use_state(|| false);
    let diff_str = use_state(|| "Easy".to_string());
    let (store, dispatch) = use_store::<StateStore>();

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

    let store_clone = store.clone();
    let dispatch_clone = dispatch.clone();
    let diff_str_clone = diff_str.clone();
    let change_difficulty = move |difficulty: u8|{
        let store = store_clone.clone();
        let dispatch = dispatch_clone.clone();
        let is_dropdown_visible = is_dropdown_visible.clone();
        let diff_str = diff_str_clone.clone();
        Callback::from(move |_ : MouseEvent| {
            let store = store.clone();
            let dispatch = dispatch.clone();
            let diff_str = diff_str.clone();
            let current_difficulty = match diff_str.as_str() {
                "Easy" => Difficulty::Easy as u8,
                "Hard" => Difficulty::Hard as u8,
                _ => return,
            };

            if difficulty == current_difficulty {
                // Difficulty hasn't changed, do nothing
                is_dropdown_visible.set(false);
                return;
            }
            if let Some(data) = &store.game_data {
                let session_id = data.session_id;
                let url = format!("{}/reset?sessionid={}&difficulty={}", BACKEND_URL, data.session_id, difficulty);
                spawn_local(async move {
                    let diff_str = diff_str.clone();
                    match Request::get(&url).send().await {
                        Ok(_) => {
                            info!("Switched AI to {:?}", difficulty);
                            diff_str.set(match difficulty {
                                1 => "Hard".to_owned(),
                                _ => "Easy".to_owned(),
                            });
                            spawn_local(async move {
                                match fetch_game_data(Some(session_id)).await {
                                    Ok(data) => {
                                        update_game_data(&dispatch, data.clone());
                                        debug!("Game data fetched successfully: {}", data.session_id);
                                    },
                                    Err(err) => error!("Failed to fetch game data: {}", err),
                                }
                            });
                        },
                        Err(err) => log::error!("Difficulty change failed: {}", err),
                    }
                });
            } else {
                log::error!("Cannot change difficulty: game data not available");
            }
            is_dropdown_visible.set(false);
        })
    };

    html! {
        <section class={style}>
            <div class="top-dropdown">
                <button class="dropdown-button" onclick={toggle_dropdown}>{&*diff_str}<span class="arrow down"></span></button>
                <ul class="dropdown-menu" style={dropdown_style}>
                    <MenuElement text={"Easy"} on_click={change_difficulty(Difficulty::Easy as u8)} />
                    <MenuElement text={"Hard"} on_click={change_difficulty(Difficulty::Hard as u8)} />
                </ul>
            </div>
        </section>
    }
}
