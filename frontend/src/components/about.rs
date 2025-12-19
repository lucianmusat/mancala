use yew::prelude::*;
use stylist::{yew::styled_component, Style};
use yew::Html;


#[styled_component(About)]
pub fn about() -> Html {
    let style = Style::new(css!(
        r#"
            .about-container {
              display: flex;
              align-items: center;
              justify-content: center;
              width: 1000px;
              margin: auto;
              background-color: #572a1b;
              font-size: 18px;
              color: #e1dbde;
              border: 20px solid #74452c;
              border-radius: 25px;
              padding: 20px;
              box-sizing: border-box;
            }

            .about-container img {
              max-width: 100%;
              max-height: 100%;
              margin-right: 20px;
            }

            .about-container p {
              flex: 1;
              margin: 0;
              text-align: left;
            }

            .about-container p a {
              color: #a13961;
            }
        "#
    )).unwrap();

    html! {
        <div class={style}>
            <div class="about-container">
                <img src="/static/static/mancala.jpg" alt="Mancala Image" />
                <p>
                    {"This little project started from a job application code challenge that I received."} <br />{"I was given a day to complete
                    it, and it wasn't very good upon completion, but I liked working on it, so I decided to continue in my spare time."}
                    <br />{"In time I added a few features, and maybe I will add more in the future, depending on how much time I have."}
                    <br /><br />{"One of the things I added is multi-session support. In the background it runs a Redis container that keeps track of players sessions."}
                    <br /><br />{"Another feature is AI player support, two different types of AI each with its own difficulty setting. The easy AI is a random strategy,
                    while the hard AI is a minimax strategy that tries to pick the best move by calculating all the moves 2 levels in the future."}
                    <br />{"The hard AI should be pretty good, but beatable."}
                    <br /><br />{"The source code can be found "}<a href="https://github.com/lucianmusat/mancala" target="_blank">{"here"}</a>
                </p>
            </div>
        </div>
    }
}