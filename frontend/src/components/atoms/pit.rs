use stylist::{yew::styled_component, Style};
use yew::prelude::*;
use crate::components::main_board::PlayerType;


#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub value: u32,
    pub player_type: PlayerType,
    pub id: u32,
    pub on_click: Callback<u32>,
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
        "#
    ))
    .unwrap();

    let on_click = {
        let on_click = props.on_click.clone();
        let id = props.id;
        Callback::from(move |_: MouseEvent| {
            on_click.emit(id);
        })
    };

    html! {
        <span class={style}>
            <div class={format!("pit {}", stones_class(props.value.clone()))} onclick={on_click} data-text={props.value.to_string()} />
        </span>
    }
}