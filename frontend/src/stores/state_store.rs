use anyhow::Error;
use reqwasm::http::Request;
use yewdux::prelude::*;
use crate::common::types::GameData;
use serde::{Serialize, Deserialize};
use uuid::Uuid;
use web_sys::window;

const SESSION_ID_STORAGE_KEY: &str = "mancala_session_id";

fn load_saved_session_id() -> Option<Uuid> {
    let window = window()?;
    let storage = window.local_storage().ok().flatten()?;
    let value = storage.get_item(SESSION_ID_STORAGE_KEY).ok().flatten()?;
    Uuid::parse_str(&value).ok()
}

fn save_session_id(id: &Uuid) {
    if let Some(window) = window() {
        if let Ok(Some(storage)) = window.local_storage() {
            let _ = storage.set_item(SESSION_ID_STORAGE_KEY, &id.to_string());
        }
    }
}

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

    // If caller didn't supply a session id, try to resume from browser storage.
    let sessionid = sessionid.or_else(load_saved_session_id);

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

    // Persist session id for future visits.
    save_session_id(&data.session_id);

    Ok(data)
}
