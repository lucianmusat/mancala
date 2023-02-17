from move import Move
from utils import MoveResult

from typing import List


class Player:

    def __init__(self, player_id: int, move_strategy: Move):
        self.id = player_id
        assert self.id in [1, 2], "Must be either player 1 or 2!"
        self.move_strategy = move_strategy

    def move(self) -> MoveResult:
        return self.move_strategy.move(self.id)

    @property
    def big_pit(self) -> int:
        return self.move_strategy.big_pit(self.id)

    @property
    def pits(self) -> List[int]:
        return self.move_strategy.pits(self.id)

    def add_stones_to_big_pit(self, stones: int) -> None:
        self.move_strategy.add_stones_to_big_pit(self.id, stones)

    def reset_all_pits(self):
        self.move_strategy.reset_all_pits(self.id)

    def collect_all_stones(self):
        self.add_stones_to_big_pit(sum(self.pits))
        self.reset_all_pits()
