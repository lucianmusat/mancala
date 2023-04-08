import os
import logging
import random

from player import IPlayer, NUMBER_OF_PITS, HAVE_TO_STEAL

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


class RandomPlayer(IPlayer):
    """
    Implementation of the Player class for a player that chooses
    the pits at random, with no strategy.
    """

    def select_pit(self, pit: int):
        pass

    def select_random_valid_pit(self):
        valid_pit_indexes = []
        for index, pit in enumerate(self.pits):
            if pit > 0:
                valid_pit_indexes.append(index)
        return random.choice(valid_pit_indexes)

    def move(self) -> (int, int):
        logging.info("Random player making a move")
        pit = self.select_random_valid_pit()
        self.selected_pit = None
        assert self.pits[pit] > 0, "Cannot move from an empty pit"
        available_stones = self.pits[pit]
        self.pits[pit] = 0
        if pit == NUMBER_OF_PITS - 1:
            return available_stones, NUMBER_OF_PITS - 1
        pit += 1
        current_pit = pit
        for i in range(pit, min(NUMBER_OF_PITS, pit + available_stones)):
            logging.info(f"Adding stone to pit {i}. Available stones: {available_stones}")
            self.pits[i] += 1
            available_stones -= 1
            current_pit = i
            if self.pits[i] == 1 and available_stones == 0:
                return HAVE_TO_STEAL, current_pit  # Landed on empty pit with last stone
        return available_stones, current_pit

    def add_stones(self, stones: int) -> int:
        assert stones > 0, "Cannot add not-positive number of stones!"
        current_pit = 0
        for i in range(0, min(NUMBER_OF_PITS, stones)):
            self.pits[i] += 1
            stones -= 1
            current_pit = i
        if self.pits[current_pit] == 1 and stones == 0:
            return HAVE_TO_STEAL
        return stones

    def collect_all_stones(self) -> None:
        logging.info("Collect all stones in the big pit")
        self.big_pit += sum(self.pits)
        self.pits = [0] * NUMBER_OF_PITS

    def steal_from(self, other_player, pit) -> None:
        logging.info(f"Stealing stones from pit {pit}")
        stones_to_steal = other_player.pits[NUMBER_OF_PITS - 1 - pit]
        other_player.pits[NUMBER_OF_PITS - 1 - pit] = 0
        self.pits[pit] = 0
        self.big_pit += stones_to_steal + 1
