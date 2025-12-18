use anyhow::Error;
use reqwasm::http::Request;
use yewdux::prelude::*;
use crate::common::types::{BACKEND_URL, GameData};
use serde::{Serialize, Deserialize};
use uuid::Uuid;
use web_sys::window;

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

    let window = window()
        .ok_or_else(|| {
            log::error!("Window object not available");
            anyhow::anyhow!("Window object not available")
        })?;

    let location = window.location();
    let origin = location.origin()
        .map_err(|err| {
            log::error!("Failed to get origin: {:?}", err);
            anyhow::anyhow!("Failed to get window origin")
        })?;
    
    let mut url = format!("{}/api/", origin);
    
    if let Some(id) = sessionid {
        url.push_str(&format!("?sessionid={}", id));
    }

    let response = Request::get(&url)
        .send()
        .await
        .map_err(|err| {
            log::error!("Request failed: {}", err);
            anyhow::anyhow!("Request failed: {}", err)
        })?;

    if !response.ok() {
        let status = response.status();
        let text = response.text().await.unwrap_or_else(|_| "Failed to read response".to_string());
        log::error!("HTTP error {}: {}", status, text);
        return Err(anyhow::anyhow!("HTTP error {}: {}", status, text));
    }

    let data = response
        .json::<GameData>()
        .await
        .map_err(|err| {
            log::error!("Failed to parse JSON: {}", err);
            anyhow::anyhow!("Failed to parse JSON: {}", err)
        })?;

    Ok(data)
}
