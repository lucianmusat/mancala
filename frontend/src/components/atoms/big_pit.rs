use stylist::{yew::styled_component, Style};
use yew::prelude::*;
use crate::common::types::PlayerType;

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub value: u32,
    pub player_type: PlayerType,
    pub reversed: bool,
}

#[styled_component(BigPit)]
pub fn pit(props: &Props) -> Html {

    let style = Style::new(css!(
        r#"
        width: 95px;
        height: 250px;
        margin-left: 15px;
        margin-top: 80px;

        .big-pit {
            width: 95px;
            height: 250px;
            text-align: center;
            vertical-align: middle;
            font-weight: bold;
            font-size: 20px;
            color: white;
        }
        "#
    ))
    .unwrap();

    let (cell_one, cell_two) = if props.reversed {
        (props.player_type.to_html(), Html::from(props.value.to_string()))
    } else {
        (Html::from(props.value.to_string()), props.player_type.to_html())
    };

    html! {
        <div class={style}>
            <table class="big-pit">
                <tr>
                    <td>{cell_one}</td>
                </tr>
                <tr>
                    <td>{cell_two}</td>
                </tr>
            </table>
        </div>
    }
}