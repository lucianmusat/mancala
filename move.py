from abc import ABC
from typing import List

from board import Board
from utils import MoveResult


class Move(ABC):

    def move(self, player_id: int) -> MoveResult:
        raise NotImplementedError

    def pits(self, player_id: int) -> List[int]:
        raise NotImplementedError

    def big_pit(self, player_id: int) -> int:
        raise NotImplementedError

    def reset_all_pits(self, player_id: int) -> None:
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

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        """
        The main game logic. Calculates how the stones will be divided
        after choosing a pit.
        :param player_id: Id of the player that moves
        :param pit: Player's pit index
        :return: If the move was valid or not, or special case when it
        landed inside its own big pit
        """
        other_player_id = 1 if player_id == 2 else 2
        available_stones = self.board.player_pits(player_id)[pit]
        assert available_stones > 0, "No stones to pick!"
        self.board.reset_pit(player_id, pit)
        # Put stones in the next pits
        while available_stones > 0:
            for i in range(pit + 1, 6):
                if available_stones > 0:
                    print(f"Adding stone to pit {i}. Available stones: {available_stones}")
                    self.board.increment_pit(player_id, i)
                    available_stones -= 1
                    # Landed on an empty pit
                    if available_stones == 0 and self.board.player_pits(player_id)[i] == 1:
                        print("Taking opponents stones")
                        self.board.reset_pit(player_id, i)
                        opposite_stones = self.board.player_pits(other_player_id)[5 - i]
                        self.board.reset_pit(other_player_id, 5 - i)
                        self.board.add_stones_to_big_pit(player_id, opposite_stones + 1)
                else:
                    break
            # If we have stones still in the hand put it in the big pit
            if available_stones > 0:
                print(f"Adding a stone to the big pit. Available stones: {available_stones}")
                self.board.increment_big_pit(player_id)
                available_stones -= 1
                # Last stone landed in own big pit
                if available_stones == 0:
                    return MoveResult.InOwnBigPit
            # If we still have stones in the hand start putting in player2 pits
            if available_stones > 0:
                for i in range(0, 6):
                    print(f"Available stones: {available_stones}. Adding a stone to the other player's pit {i}")
                    self.board.increment_pit(other_player_id, i)
                    available_stones -= 1
                    if available_stones == 0:
                        break
            # Still have stones, need to start from the beginning
            if available_stones > 0:
                print(f"Still have stones left: {available_stones}, starting over")
                pit = -1
        return MoveResult.Valid

    # Move base class implementation

    def move(self, player_id: int) -> MoveResult:
        # This is a human player move, so we get the result from the user
        pit = input(f"Player {player_id} move [1-6]: ")
        if not pit.isnumeric():
            return MoveResult.Invalid
        # Because we chose 1 based
        pit = int(pit) - 1
        if not self.legal_move(player_id, pit):
            return MoveResult.Invalid
        return self.move_pit(player_id, pit)

    def pits(self, player_id: int) -> List[int]:
        return self.board.player_pits(player_id)

    def big_pit(self, player_id: int) -> int:
        return self.board.player_big_pit(player_id)

    def reset_all_pits(self, player_id: int) -> None:
        self.board.reset_all_pits(player_id)

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        self.board.add_stones_to_big_pit(player_id, stones)
