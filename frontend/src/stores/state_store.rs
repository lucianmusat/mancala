use anyhow::Error;
use reqwasm::http::Request;
use yewdux::prelude::*;
use crate::common::types::{BACKEND_URL, GameData};
use serde::{Serialize, Deserialize};
use uuid::Uuid;
use url::Url;

#[derive(Debug, Default, Clone, PartialEq, Serialize, Deserialize, Store)]
pub struct StateStore {
    pub game_data: Option<GameData>
}

pub fn update_game_data(dispatch: &Dispatch<StateStore>, game_data: GameData) {
    dispatch.reduce_mut(|state| {
        state.game_data = Some(game_data.clone());
    });
}

pub async fn fetch_game_data(sessionid: Option<Uuid>) -> Result<GameData, Error> {
    let mut url = Url::parse(BACKEND_URL).map_err(|err| anyhow::anyhow!("Invalid URL: {}", err))?;

    if let Some(id) = sessionid {
        url.query_pairs_mut().append_pair("sessionid", &id.to_string());
    }

    let response = Request::get(url.as_str())
        .send()
        .await
        .map_err(|err| anyhow::anyhow!("Request failed: {}", err))?;

    let data = response
        .json::<GameData>()
        .await
        .map_err(|err| anyhow::anyhow!("Failed to parse JSON: {}", err))?;

    Ok(data)
}
