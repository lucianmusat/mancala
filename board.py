import os
import logging
import dataclasses
from typing import List

STARTING_STONES = 6
NUMBER_OF_PITS = 6
NO_WINNER = None


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
        print(f"Player {player} moving from pit {pit}")
        if not self.is_valid_pit(pit) or not self.has_available_stones(self.players_data[player], pit):
            return False
        available_stones = self.players_data[player].pits[pit]
        original_player = player
        self.players_data[player].pits[pit] = 0
        while available_stones > 0:
            if pit < NUMBER_OF_PITS - 1:
                pit += 1
                available_stones = self.add_stone(player, pit, available_stones)
                logging.debug(f"Adding stone to pit {pit}. Available stones: {available_stones}")
                # Landed on own empty pit with last stone, steal the stones from the opposite player's pit
                if self.players_data[player].pits[pit] == 1 and available_stones == 0 and player == original_player:
                    self.steal_stones(player, pit)
            if self.reached_end(pit, available_stones):
                pit = -1
                available_stones = self.landed_on_own_big_pit(player, available_stones, player == original_player)
                if available_stones != 0:
                    logging.debug(f"Player {player} continues in opponent's pits")
                    player = self.switch_player(player)
                else:
                    # Landed on own big pit with the last stone. We can go again
                    return False
        return True

    @staticmethod
    def reached_end(pit: int, available_stones: int) -> bool:
        """
        Checks if the end of the pits has been reached.
        """
        return pit == NUMBER_OF_PITS - 1 and available_stones > 0

    def landed_on_own_big_pit(self, player: int, available_stones: int, own_pit: bool) -> int:
        """
        Adds a stone to the player's big pit and returns the number of remaining stones.
        """

        if own_pit:
            self.players_data[player].big_pit += 1
            available_stones -= 1
        return available_stones

    @staticmethod
    def switch_player(player: int) -> int:
        """
        Switches the player to the opponent.
        """
        return 1 - player

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
            f"There was a problem in the stone moves! {self.nr_players * NUMBER_OF_PITS * STARTING_STONES} " \
            f"expected stones on the board," \
            f" {all_stones_on_board} stones on board. Player1 pits: " \
            f"{self.players_data[0].pits} Player2 pits: {self.players_data[1].pits} Player1 big pit: " \
            f"{self.players_data[0].big_pit} Player2 big pit: {self.players_data[1].big_pit}"

        if self.any_player_finished():
            for player_index in range(self.nr_players):
                self.collect_all_stones(player_index)
            return max(range(self.nr_players), key=lambda i: self.players_data[i].big_pit)
        return NO_WINNER

    def game_over(self) -> bool:
        """
        Checks if the game is over.
        """
        return self.winner != NO_WINNER

    def any_player_finished(self):
        """
        Checks if any player has finished the game.
        """
        for player_index in range(self.nr_players):
            if all(stones == 0 for stones in self.players_data[player_index].pits):
                return True
        return False

    def evaluate(self, player_index: int):
        """
        Evaluates the board for the given player.
        Here we need to evaluate the state of the board and make a
        judgement of how good it is for the player
        :param player_index: the index of the player for which we evaluate the board
        """
        # simple algorithm, who has more points in the end
        logging.debug(f"Evaluate time, player has {self.players_data[player_index].big_pit} stones in big pit "
                      f"{self.players_data[player_index].pits} and opponent has "
                      f"{self.players_data[1- player_index].big_pit} stones in big pit "
                      f"{self.players_data[1 - player_index].big_pit}")
        return self.players_data[player_index].big_pit - self.players_data[1 - player_index].big_pit

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
        :param player: The player for which the list of valid pit indexes is returned.
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

    def __str__(self) -> str:
        str_rep = ""
        for index, player in enumerate(self.players_data):
            str_rep += f"Player {index} has {player.big_pit} stones in big pit and {player.pits} stones in pits"
        return str_rep
