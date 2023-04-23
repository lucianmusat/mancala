import os
import logging
import random

import board
from player import IPlayer

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


class RandomPlayer(IPlayer):
    """
    Implementation of the Player class for a player that chooses
    the pits at random, with no strategy.
    """

    def __init__(self, index: int, game_board: board.Board):
        self.index = index
        self.board = game_board
        logging.info(f"Random player {index} created")

    def move(self) -> bool:
        logging.info("Random player making a move")
        return self.board.move(self.index, random.choice(self.board.valid_pit_indexes(self.index)))
