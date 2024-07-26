use yewdux::prelude::*;
use crate::common::types::{GameData};

#[derive(Store, Default, PartialEq)]
pub struct StateStore {
    pub game_data: GameData
}