import os
import logging

from player import IPlayer
import board

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


class HumanPlayer(IPlayer):
    """
    Implementation of the Player class for a player that chooses
    the pits by clicking on them in the web interface.
    """

    def __init__(self, index: int, game_board: board.Board):
        self.selected_pit = None
        self.index = index
        self.board = game_board
        logging.info(f"Human player {index} created")

    def select_pit(self, pit: int) -> None:
        self.selected_pit = pit

    def move(self) -> bool:
        assert self.selected_pit is not None, "No pit selected!"
        return self.board.move(self.index, self.selected_pit)

