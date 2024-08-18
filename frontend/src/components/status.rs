use yew::prelude::*;
use stylist::{yew::styled_component, Style};
use yewdux::use_store;
use crate::common::types::PlayerType;
use crate::stores::state_store::StateStore;


#[styled_component(Status)]
pub fn status() -> Html {
    let (store, _) = use_store::<StateStore>();

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

    let visible = is_visible(&store);
    html! {
        <div class={style} hidden={!visible}>
            <p class="neonText">{winner_text(&store)}</p>
        </div>
    }
}

fn winner_to_string(winner: &Option<PlayerType>) -> String {
    match winner {
        Some(PlayerType::Player1) => "Player 1".to_string(),
        Some(PlayerType::Player2) => "Player 2".to_string(),
        None => "No one".to_string(),
    }
}

fn is_visible(store: &StateStore) -> bool {
    if store.game_data.as_ref().is_some() && store.game_data.as_ref().unwrap().winner.is_some() {
        true
    } else {
       false
    }
}

fn winner_text(store: &StateStore) -> String {
    let winner = store.game_data.as_ref().map(|data| &data.winner).unwrap_or(&None);
    if winner.is_none() {
        return "".to_string();
    }
    format!("{} wins!", winner_to_string(winner))
}