use std::collections::HashMap;
use stylist::{yew::styled_component, Style};
use yew::prelude::*;
use crate::components::main_board::PlayerType;

const FRONTEND_URL: &str = "http://localhost:8080";

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub value: u32,
    pub player_type: PlayerType,
    pub id: u32,
    pub on_click: Callback<MouseEvent>,
}

#[styled_component(Pit)]
pub fn pit(props: &Props) -> Html {

    fn stones_class(value: u32) -> String {
        match value {
            value if value > 6 || value < 0 => "multiple-stones".to_string(),
            value if value >=0 && value <= 6 => format!("stones-{}", value),
            _ => "".to_string(),
        }
    }

    let style = Style::new(css!(
        r#"
            .pit {
                display: inline-block;
                width: 50px;
                height: 50px;
                text-align: center;
                line-height: 50px;
                font-size: 24px;
                font-family: Arial, Helvetica, sans-serif;
                font-weight: bold;
            }

            .pit:hover {
                cursor: pointer;
                filter: brightness(150%);
            }
        "#
    ))
    .unwrap();

    html! {
        <span class={style}>
            <div class={format!("pit {}", stones_class(props.value.clone()))} onclick={&props.on_click}>
                {props.value}
            </div>
        </span>
    }
}