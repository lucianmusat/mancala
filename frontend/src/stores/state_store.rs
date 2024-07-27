use yewdux::prelude::*;
use crate::common::types::GameData;
use serde::{Serialize, Deserialize};

#[derive(Debug, Default, Clone, PartialEq, Serialize, Deserialize, Store)]
pub struct StateStore {
    pub game_data: Option<GameData>
}

pub fn update_game_data(dispatch: &Dispatch<StateStore>, game_data: GameData) {
    dispatch.reduce_mut(|state| {
        state.game_data = Some(game_data.clone());
    });
}
