import os
import logging
from abc import ABC

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class Player(ABC):

    def __init__(self):
        self.big_pit = 0
        self.pits = [6] * 6

    def move(self, pit: int) -> (int, int):
        raise NotImplementedError

    def add_stones(self, stones: int) -> int:
        raise NotImplementedError

    def collect_all_stones(self):
        raise NotImplementedError

    def steal_from(self, other_player, pit):
        raise NotImplementedError

    def reset(self):
        self.__init__()


class HumanPlayer(Player):

    def move(self, pit: int) -> (int, int):
        assert self.pits[pit] > 0, "Cannot move from an empty pit"
        available_stones = self.pits[pit]
        self.pits[pit] = 0
        if pit == 5:
            return available_stones, 5
        pit += 1
        current_pit = pit
        for i in range(pit, min(6, pit + available_stones)):
            logging.info(f"Adding stone to pit {i}. Available stones: {available_stones}")
            self.pits[i] += 1
            available_stones -= 1
            current_pit = i
            if self.pits[i] == 1 and available_stones == 0:
                return -1, current_pit  # Landed on empty pit with last stone
        return available_stones, current_pit

    def add_stones(self, stones: int) -> int:
        assert stones > 0, "Cannot add not-positive number of stones!"
        current_pit = 0
        for i in range(0, min(6, stones)):
            self.pits[i] += 1
            stones -= 1
            current_pit = i
        if self.pits[current_pit] == 1 and stones == 0:
            return -1
        return stones

    def collect_all_stones(self) -> None:
        logging.info("Collect all stones in the big pit")
        self.big_pit += sum(self.pits)
        self.pits = [0] * 6

    def steal_from(self, other_player, pit) -> None:
        logging.info(f"Stealing stones from pit {pit}")
        stones_to_steal = other_player.pits[5 - pit]
        other_player.pits[5 - pit] = 0
        self.pits[pit] = 0
        self.big_pit += stones_to_steal + 1

