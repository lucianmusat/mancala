import os
import logging
from typing import List

from utils import MoveResult

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class Board:
    """
    Class that represents the game board.
    It keeps track of each pit and stones.
    """

    def __init__(self):
        self.internal_player_pits = {1: [6] * 6, 2: [6] * 6}
        self.internal_player_big_pit = {1: 0, 2: 0}

    def player_big_pit(self, player_id: int) -> int:
        return self.internal_player_big_pit[player_id]

    def player_pits(self, player_id: int) -> List[int]:
        return self.internal_player_pits[player_id]

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        assert stones > 0
        self.internal_player_big_pit[player_id] += stones

    def add_stones_to_pit(self, player_id: int, index: int, stones: int) -> None:
        assert stones > 0
        self.internal_player_pits[player_id][index] += stones

    def increment_pit(self, player_id: int, index: int) -> None:
        self.add_stones_to_pit(player_id, index, 1)

    def increment_big_pit(self, player_id: int) -> None:
        self.add_stones_to_big_pit(player_id, 1)

    def reset_pit(self, player_id: int, index: int) -> None:
        self.internal_player_pits[player_id][index] = 0

    def clear_all_small_pits(self, player_id: int) -> None:
        self.internal_player_pits[player_id] = [0] * 6

    def reset_board(self) -> None:
        self.internal_player_pits = {1: [6] * 6, 2: [6] * 6}
        self.internal_player_big_pit = {1: 0, 2: 0}

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        """
        The main game logic. Calculates how the stones will be divided
        after choosing a pit.
        :param player_id: Id of the player that made the move
        :param pit: Player's pit index
        :return: If the move was valid or not, or special case when it
        landed inside its own big pit
        """
        other_player_id = 1 if player_id == 2 else 2
        available_stones = self.internal_player_pits[player_id][pit]
        assert available_stones > 0, "No stones to pick!"
        self.reset_pit(player_id, pit)
        # Put stones in the next pits
        while available_stones > 0:
            for i in range(pit + 1, 6):
                if available_stones > 0:
                    logging.debug(f"Adding stone to pit {i}. Available stones: {available_stones}")
                    self.increment_pit(player_id, i)
                    available_stones -= 1
                    # Landed on an empty pit
                    if available_stones == 0 and self.internal_player_pits[player_id][i] == 1:
                        logging.debug("Taking opponents stones")
                        self.reset_pit(player_id, i)
                        opposite_stones = self.player_pits(other_player_id)[5 - i]
                        self.reset_pit(other_player_id, 5 - i)
                        self.add_stones_to_big_pit(player_id, opposite_stones + 1)
                else:
                    break
            # If we have stones still in the hand put it in the big pit
            if available_stones > 0:
                logging.debug(f"Adding a stone to the big pit. Available stones: {available_stones}")
                self.increment_big_pit(player_id)
                available_stones -= 1
                # Last stone landed in own big pit
                if available_stones == 0:
                    return MoveResult.InOwnBigPit
            # If we still have stones in the hand start putting in player2 pits
            if available_stones > 0:
                for i in range(0, 6):
                    logging.debug(f"Available stones: {available_stones}. Adding a stone to the other player's pit {i}")
                    self.increment_pit(other_player_id, i)
                    available_stones -= 1
                    if available_stones == 0:
                        break
            # Still have stones, need to start from the beginning
            if available_stones > 0:
                pit = -1
        return MoveResult.Valid
