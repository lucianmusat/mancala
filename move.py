from abc import ABC
from typing import List

from board import Board
from utils import MoveResult


class Move(ABC):

    def move(self, player_id: int) -> MoveResult:
        raise NotImplementedError

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        raise NotImplementedError

    def pits(self, player_id: int) -> List[int]:
        raise NotImplementedError

    def big_pit(self, player_id: int) -> int:
        raise NotImplementedError

    def clear_all_small_pits(self, player_id: int) -> None:
        raise NotImplementedError

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        raise NotImplementedError


class HumanMove(Move):

    def __init__(self, board: Board):
        self.board = board

    def legal_move(self, player_id: int, pit: int) -> bool:
        if pit not in range(0, 6):
            input(f"Illegal move, {pit} must be in range 1..6!")
            return False
        if self.board.player_pits(player_id)[pit] == 0:
            input(f"The pit {pit} does not contain any stones!")
            return False
        return True

    # Move base class implementation

    def move(self, player_id: int) -> MoveResult:
        raise NotImplementedError

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        # This is a human player move, so we get the result from the user
        # pit = input(f"Player {player_id} move [1-6]: ")
        # if not pit.isnumeric():
        #     return MoveResult.Invalid
        # # Because we chose 1 based
        # pit = int(pit) - 1
        if not self.legal_move(player_id, pit):
            return MoveResult.Invalid
        return self.board.move_pit(player_id, pit)

    def pits(self, player_id: int) -> List[int]:
        return self.board.player_pits(player_id)

    def big_pit(self, player_id: int) -> int:
        return self.board.player_big_pit(player_id)

    def clear_all_small_pits(self, player_id: int) -> None:
        self.board.clear_all_small_pits(player_id)

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        self.board.add_stones_to_big_pit(player_id, stones)
