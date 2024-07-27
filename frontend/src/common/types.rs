use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub(crate) const BACKEND_URL: &str = "http://localhost:8000";

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub enum PlayerType {
    #[default]
    #[serde(rename = "0")]
    Player1 = 0,
    #[serde(rename = "1")]
    Player2 = 1
}

impl PartialEq for PlayerType {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (PlayerType::Player1, PlayerType::Player1) => true,
            (PlayerType::Player2, PlayerType::Player2) => true,
            _ => false,
        }
    }
}

impl From<PlayerType> for u32 {
    fn from(player_type: PlayerType) -> u32 {
        match player_type {
            PlayerType::Player1 => 0,
            PlayerType::Player2 => 1
        }
    }
}

#[derive(Debug, Clone, PartialEq, Default, Serialize, Deserialize)]
pub enum Difficulty {
    #[default]
    #[serde(rename = "0")]
    Easy = 0,
    #[serde(rename = "1")]
    Hard = 1,
}

impl From<Difficulty> for u32 {
    fn from(difficulty: Difficulty) -> u32 {
        match difficulty {
            Difficulty::Easy => 0,
            Difficulty::Hard => 1,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct Player {
    pub big_pit: u32,
    pub pits: Vec<u32>,
}

#[derive(Serialize, Deserialize, Debug, Clone, Default, PartialEq)]
#[serde(rename_all = "snake_case")]
pub struct GameData {
    pub session_id: Uuid,
    pub difficulty: Difficulty,
    pub turn: PlayerType,
    pub winner: Option<PlayerType>,
    pub players: HashMap<u32, Player>
}
