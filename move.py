from abc import ABC
from typing import List

from board import Board
from utils import MoveResult


class Move(ABC):
    """
    Template describing a move strategy that a player can implement.
    """

    def move(self, player_id: int) -> MoveResult:
        """
        A pit number is not provided.
        Can be used in case of AI players, to decide which
        pit to play next.
        :param player_id: Either player 1 or 2
        :return: The move was valid or not
        """
        raise NotImplementedError

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        """
        Can be used either for human players, where the choice
        is done somewhere else (ex. the web interface, CLI etc.)
        or for testing.
        :param player_id: Either player 1 or 2
        :param pit: The pit index to be played
        :return: The move was valid or not
        """
        raise NotImplementedError

    def pits(self, player_id: int) -> List[int]:
        """
        :param player_id: Either player 1 or 2
        :return: The current status of the player's pits
        """
        raise NotImplementedError

    def big_pit(self, player_id: int) -> int:
        """
        :param player_id: Either player 1 or 2
        :return: The current status of the player's big pit
        """
        raise NotImplementedError

    def clear_all_small_pits(self, player_id: int) -> None:
        """
        Set all the player's pits to 0. Used at games' end
        when the board is cleared.
        :param player_id: Either player 1 or 2
        :return: None
        """
        raise NotImplementedError

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        """
        Add a number of stones to the player's big pit.
        :param player_id: Either player 1 or 2
        :param stones: Number of stones to add
        :return: None
        """
        raise NotImplementedError


class HumanMove(Move):
    """
    Implementation of the Move interface for
    a human player
    """

    def __init__(self, board: Board):
        self.board = board

    def legal_move(self, player_id: int, pit: int) -> bool:
        """
        Check weather a chosen move is legal or not. If the pit
        index is correct and there are stones to pick from it then
        it's legal.
        :param player_id: Either player 1 or 2
        :param pit: Player's pit index
        :return: True if move is legal, otherwise False
        """
        if pit not in range(0, 6) or self.board.player_pits(player_id)[pit] == 0:
            return False
        return True

    # Move base class implementation

    def move(self, player_id: int) -> MoveResult:
        raise NotImplementedError

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        # This is a human player move, so we get the result from the user
        if self.legal_move(player_id, pit):
            return self.board.move_pit(player_id, pit)
        return MoveResult.Invalid

    def pits(self, player_id: int) -> List[int]:
        return self.board.player_pits(player_id)

    def big_pit(self, player_id: int) -> int:
        return self.board.player_big_pit(player_id)

    def clear_all_small_pits(self, player_id: int) -> None:
        self.board.clear_all_small_pits(player_id)

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        self.board.add_stones_to_big_pit(player_id, stones)
