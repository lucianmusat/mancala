use yew::prelude::*;
use stylist::{yew::styled_component, Style};

#[styled_component(Logo)]
pub fn menu_element() -> Html {
    let style =  Style::new(css!(
        r#"
            div {
                display: inline-block;
                text-align: center;
                font-size: 128px;
                font-family: 'dk_jambo-regular', sans-serif;
                font-weight: bold;
                color: #FDFEFF;
                text-shadow: 3px 3px 5px #000;
                margin-left: 200px;
            }
        "#
    ))
        .unwrap();

    html! {
        <section class={style}>
            <div> {"Mancala"} </div>
        </section>
    }
}