from abc import ABC, abstractmethod


STARTING_STONES = 6
NUMBER_OF_PITS = 6
HAVE_TO_STEAL = -1
NO_WINNER = -1
INVALID_CHOICE = -2


class IPlayer(ABC):
    """
    A Player interface that is being used by the
    Game class.
    """

    def __init__(self):
        self.big_pit = 0
        self.pits = [STARTING_STONES] * NUMBER_OF_PITS
        self.selected_pit = None

    @abstractmethod
    def select_pit(self, pit: int):
        """
        Select which pit to move from next.
        May not be used by AI players.
        Human players receive the pit index from the web interface.
        :param pit: Chosen pit index
        """
        ...

    @abstractmethod
    def move(self) -> (int, int):
        """
        Chose a pit to move from.
        For human players it works with the pit selected in the select_next_move() method.
        For AI players it contains the logic to choose the pit.
        :return: A tuple expressing the available stones left after finishing
        the move and the current pit. If the last stone landed on an empty pit
        then the available stones is set to -1
        """
        ...

    @abstractmethod
    def add_stones(self, stones: int) -> int:
        """
        Increment the current pits with the number of stones.
        :param stones: Number of stones available
        :return: Remaining stones after a pass of increments.
        If the last stone landed on an empty pit then return -1
        """
        ...

    @abstractmethod
    def collect_all_stones(self):
        """
        Gather all the stones from all the pits and
        add them to the big pit.
        :return: None
        """
        ...

    @abstractmethod
    def steal_from(self, other_player, pit):
        """
        Steal the stones from the other player's opposite pit.
        :param other_player: The opposing player
        :param pit: Pit index of current player
        :return: None
        """
        ...

    def reset(self):
        """
        Return player's pits to the initial values.
        :return: None
        """
        self.__init__()
