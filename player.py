import os
import logging
from abc import ABC

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))

STARTING_STONES = 6
NUMBER_OF_PITS = 6


class Player(ABC):
    """
    A Player interface that is being used by the
    Game class.
    """

    def __init__(self):
        self.big_pit = 0
        self.pits = [STARTING_STONES] * NUMBER_OF_PITS

    def move(self, pit: int) -> (int, int):
        """
        Chose a pit to move from. In this case we
        receive the pit index from the web interface.
        :param pit: Chosen pit index
        :return: A tuple expressing the available stones left after finishing
        the move and the current pit. If the last stone landed on an empty pit
        then the available stones is set to -1
        """
        raise NotImplementedError

    def add_stones(self, stones: int) -> int:
        """
        Increment the current pits with the number of stones.
        :param stones: Number of stones available
        :return: Remaining stones after a pass of increments.
        If the last stone landed on an empty pit then return -1
        """
        raise NotImplementedError

    def collect_all_stones(self):
        """
        Gather all the stones from all the pits and
        add them to the big pit.
        :return: None
        """
        raise NotImplementedError

    def steal_from(self, other_player, pit):
        """
        Steal the stones from the other player's opposite pit.
        :param other_player: The opposing player
        :param pit: Pit index of current player
        :return: None
        """
        raise NotImplementedError

    def reset(self):
        """
        Return player's pits to the initial values.
        :return: None
        """
        self.__init__()


class HumanPlayer(Player):
    """
    Implementation of the Player class for a player that chooses
    the pits by clicking on them in the web interface.
    """

    def move(self, pit: int) -> (int, int):
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
                return -1, current_pit  # Landed on empty pit with last stone
        return available_stones, current_pit

    def add_stones(self, stones: int) -> int:
        assert stones > 0, "Cannot add not-positive number of stones!"
        current_pit = 0
        for i in range(0, min(NUMBER_OF_PITS, stones)):
            self.pits[i] += 1
            stones -= 1
            current_pit = i
        if self.pits[current_pit] == 1 and stones == 0:
            return -1
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
