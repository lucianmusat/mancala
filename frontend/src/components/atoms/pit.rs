use stylist::{yew::styled_component, Style};
use yew::prelude::*;
use crate::common::types::PlayerType;


#[derive(Clone, PartialEq)]
pub struct ClickData {
    pub player_type: PlayerType,
    pub id: u32,
}

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub value: u32,
    pub player_type: PlayerType,
    pub id: u32,
    pub on_click: Callback<ClickData>,
    pub disabled: bool,
}

#[styled_component(Pit)]
pub fn pit(props: &Props) -> Html {

    fn stones_class(value: u32) -> String {
        match value {
            value if value > 6 => "multiple_stones".to_string(),
            value if value <= 6 => format!("stones-{}", value),
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
                font-size: 18px;
                font-family: Arial, Helvetica, sans-serif;
                font-weight: bold;
                color: white;
            }

            .pit:hover {
                cursor: pointer;
                filter: brightness(150%);
            }

            .pit::before {
                content: attr(data-text);
                display: block;
                transform: translateY(65px);
            }

            .pit:not(.disabled):hover {
                cursor: pointer;
                filter: brightness(150%);
            }

            .pit.disabled {
                opacity: 0.5;
                cursor: default;
            }
        "#
    ))
    .unwrap();

    let properties = props.clone();
    let on_click = Callback::from(move |e: MouseEvent| {
        if !properties.disabled {
            let on_click = properties.on_click.clone();
            let id = properties.id;
            let player_type = properties.player_type.clone();
            on_click.emit(ClickData { player_type, id });
        }
        e.prevent_default();
        });

    let pit_class = classes!("pit", stones_class(props.value.clone()), if props.disabled { "disabled" } else { "" });

    html! {
        <span class={style}>
            <div class={pit_class} onclick={on_click} data-text={props.value.to_string()} />
        </span>
    }
}