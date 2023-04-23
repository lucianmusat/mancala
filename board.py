import os
import logging
import dataclasses
from typing import List

STARTING_STONES = 6
NUMBER_OF_PITS = 6
NO_WINNER = -1


logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


@dataclasses.dataclass
class PlayerData:
    big_pit: int = 0
    pits: List[int] = dataclasses.field(default_factory=lambda: [STARTING_STONES] * NUMBER_OF_PITS)


class Board:
    """
    The class that manages the board state. Keeps track of all the pits, big pits
    and the stones.
    """
    def __init__(self, nr_players: int):
        self.nr_players = nr_players
        self.players_data = []
        for i in range(self.nr_players):
            self.players_data.append(PlayerData())

    def move(self, player: int, selected_pit: int) -> bool:
        """
        Moves the stones from the selected pit.
        :param player: The player that is making the move
        :param selected_pit: The pit from which the stones are moved
        :return: the return value of move_from
        """
        logging.info(f"Player {player} selected pit {selected_pit}")
        return self.move_from(player, selected_pit)

    def move_from(self, player: int, pit: int) -> bool:
        """
        Moves the stones from the given pit.
        :param player: The player that is making the move
        :param pit: The pit from which the stones are moved
        :return: True if the move was successful, False otherwise or if the game is over,
        or if the player has no stones in the selected pit, or if the same player can go again.
        """
        if not self.is_valid_pit(pit) or not self.has_available_stones(self.players_data[player], pit):
            return False
        available_stones = self.players_data[player].pits[pit]
        original_player = player
        max_pit_index = NUMBER_OF_PITS - 1
        self.players_data[player].pits[pit] = 0
        while available_stones > 0:
            if pit < max_pit_index:
                pit += 1
                available_stones = self.add_stone(player, pit, available_stones)
                logging.debug(f"Adding stone to pit {pit}. Available stones: {available_stones}")
                logging.debug(f"player's current pits: {self.players_data[player].pits}")
                # Landed on own empty pit with last stone, steal the stones from the opposite player's pit
                if self.players_data[player].pits[pit] == 1 and available_stones == 0 and original_player == player:
                    logging.debug(f"Player {player} landed on empty pit {pit}")
                    self.steal_stones(player, pit)
            if pit == max_pit_index and available_stones > 0:
                pit = -1
                # Landed on own big pit
                if original_player == player:
                    logging.debug(f"Player {player} landed on big pit")
                    self.players_data[player].big_pit += 1
                    available_stones -= 1
                # Landed on own big pit with the last stone. We can go again
                if available_stones == 0:
                    return False
                else:
                    logging.debug(f"Player {player} continues in opponent's pits")
                    player = 1 - player
        return True

    def opponent(self, player):
        """
        Returns the opponent of the given player.
        """
        return self.players_data[1 - player]

    def steal_stones(self, player: int, pit: int):
        """
        Steals the stones from the opposite player's pit.
        """
        logging.info(f"Stealing stones from pit {pit}")
        stones_to_steal = self.opponent(player).pits[NUMBER_OF_PITS - 1 - pit]
        self.opponent(player).pits[NUMBER_OF_PITS - 1 - pit] = 0
        self.players_data[player].pits[pit] = 0
        self.players_data[player].big_pit += stones_to_steal + 1

    def collect_all_stones(self, player: int):
        """
        Collects all remaining stones from the player's pits.
        """
        for i in range(0, NUMBER_OF_PITS):
            self.players_data[player].big_pit += self.players_data[player].pits[i]
            self.players_data[player].pits[i] = 0

    @property
    def winner(self) -> int:
        """
        Checks if the game is over and returns the winner.
        """
        all_stones_on_board = 0
        for player_index in range(self.nr_players):
            all_stones_on_board += self.players_data[player_index].big_pit
            for pit in self.players_data[player_index].pits:
                all_stones_on_board += pit

        assert all_stones_on_board == self.nr_players * NUMBER_OF_PITS * STARTING_STONES, \
            f"There was a problem in the stone moves! {self.nr_players * NUMBER_OF_PITS * STARTING_STONES} expected stones on the board," \
            f" {all_stones_on_board} stones on board. Player1 pits: " \
            f"{self.players_data[0].pits} Player2 pits: {self.players_data[1].pits} Player1 big pit: " \
            f"{self.players_data[0].big_pit} Player2 big pit: {self.players_data[1].big_pit}"

        if self.any_player_finished():
            for player_index in range(self.nr_players):
                self.collect_all_stones(player_index)
            return max(range(self.nr_players), key=lambda i: self.players_data[i].big_pit)
        return NO_WINNER

    def any_player_finished(self):
        for player_index in range(self.nr_players):
            if all(stones == 0 for stones in self.players_data[player_index].pits):
                return True
        return False

    def reset(self):
        """
        Resets the board to the initial state.
        """
        for player in self.players_data:
            player.big_pit = 0
            player.pits = [STARTING_STONES] * NUMBER_OF_PITS

    def valid_pit_indexes(self, player: int) -> List[int]:
        """
        Returns a list of valid pit indexes for the given player.
        """
        return [i for i, stones in enumerate(self.players_data[player].pits) if stones > 0]

    @staticmethod
    def is_valid_pit(pit: int) -> bool:
        """
        Checks if the pit is a valid index in the game board.
        :param pit: The pit to be checked.
        :return: True if the pit is valid, False otherwise.
        """
        return pit in range(0, NUMBER_OF_PITS)

    @staticmethod
    def has_available_stones(player_data: PlayerData, pit: int) -> bool:
        """
        Checks if there are stones available in the given pit.
        :param player_data: The data for the current player.
        :param pit: The pit to be checked.
        :return: True if there are available stones, False otherwise.
        """
        return player_data.pits[pit] != 0

    def add_stone(self, player: int, pit: int, available_stones: int) -> int:
        """
        Adds a stone to the given pit.
        :param player: The player that is making the move.
        :param pit: The pit to which the stone is added.
        :param available_stones: The number of available stones.
        """
        self.players_data[player].pits[pit] += 1
        available_stones -= 1
        return available_stones
