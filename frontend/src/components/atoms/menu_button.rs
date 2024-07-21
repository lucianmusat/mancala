use stylist::{yew::styled_component, Style};
use yew::prelude::*;

#[derive(Properties, Clone, PartialEq)]
pub struct Props {
    pub text: String,
    pub on_click: Callback<MouseEvent>,
}

#[styled_component(MenuButton)]
pub fn menu_button(props: &Props) -> Html {
    let style =  Style::new(css!(
        r#"
            a {
                float: left;
                margin-left: 50px;
                text-align: center;
                line-height: 100px;
                font-size: 42px;
                font-family: Arial, Helvetica, sans-serif;
                font-weight: bold;
                color: #231E1F;
            }

            a:hover {
                color: #7C636E;
                cursor: pointer;
            }
        "#
    ))
    .unwrap();

    html! {
        <span class={style}>
            <a onclick={&props.on_click}> {&props.text} </a>
        </span>
    }
}