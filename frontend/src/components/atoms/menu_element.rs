use yew::prelude::*;
use web_sys::MouseEvent;
use stylist::{yew::styled_component, Style};


#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub text: String,
    pub on_click: Callback<MouseEvent>
}

#[styled_component(MenuElement)]
pub fn menu_element(props: &Props) -> Html {
    let style =  Style::new(css!(
        r#"
            li {
                padding: 10px;
            }

            li a {
                color: black;
                text-decoration: none;
            }

            li:hover {
                cursor: pointer;
                background-color: #f1f1f1;
            }
        "#
    ))
    .unwrap();

    html! {
        <span class={style}>
            <li onclick={&props.on_click}> {&props.text} </li>
        </span>
    }
}