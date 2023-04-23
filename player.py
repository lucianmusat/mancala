import os
import logging

from typing import Protocol


logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


class IPlayer(Protocol):
    """
    A Player interface that is being used by the Game class.
    """

    def move(self) -> int:
        """
        Chose a pit to move from.
        For human players it simply returns the pit selected in the select_pit() method.
        For AI players it contains the logic to choose the pit.
        :return: The pit index to move from.
        """
        ...
