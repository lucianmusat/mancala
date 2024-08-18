use yew::prelude::*;
use stylist::{yew::styled_component, Style};
use yew::Html;


#[styled_component(NotFound)]
pub fn status() -> Html {
    let style = Style::new(css!(
        r#"
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 200px;
            margin-bottom: 20px;
            margin-top: 10px;
            text-align: center;
            line-height: 100px;
            font-size: 42px;
            font-family: Arial, Helvetica, sans-serif;
            color: #FDFEFF;

            .neonText {
              color: #fff;
                text-shadow:
                  0 0 4px #fff,
                  0 0 10px #fff,
                  0 0 18px #fff,
                  0 0 38px #f09,
                  0 0 73px #f09,
                  0 0 80px #f09,
                  0 0 94px #f09,
                  0 0 140px #f09;
            }
        "#
    )).unwrap();

    html! {
        <div class={style}>
            <p class="neonText">
                {"404 Not Found"}
            </p>
        </div>
        }
}