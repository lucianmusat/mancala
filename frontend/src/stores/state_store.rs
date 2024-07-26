use yewdux::prelude::*;
use crate::common::types::{GameData};

// TODO: use this?
#[derive(Store, Default, PartialEq)]
pub struct StateStore {
    pub game_data: GameData
}