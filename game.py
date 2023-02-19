import os
import logging
from typing import Dict

from player import Player


logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))


class Game:

    def __init__(self, players: Dict[int, Player]):
        self.players = players

    def check_win(self) -> int:
        assert self.players[0].big_pit + self.players[1].big_pit + \
               sum(self.players[0].pits) + sum(self.players[1].pits) == 72, f"There was a problem in the stone moves!"
        if all(stones == 0 for stones in self.players[0].pits) or all(stones == 0 for stones in self.players[1].pits):
            for player in self.players.values():
                player.collect_all_stones()
            return 0 if self.players[0].big_pit > self.players[1].big_pit else 1
        return -1

    def calculate_move(self, user_id: int, pit: int, turn: int) -> (int, int):
        logging.info(f"Click on user {user_id} pit {pit}")
        if 0 < self.players[user_id].pits[pit] and (turn % 2 == user_id):
            remaining_stones, current_pit = self.players[user_id].move(pit)
            while remaining_stones != 0:
                logging.info(f"Remaining stones: {remaining_stones} current pit: {current_pit}")
                if remaining_stones == -1:
                    self.players[user_id].steal_from(self.players[1 - user_id], current_pit)
                    remaining_stones = 0
                elif current_pit == 5 and remaining_stones > 0:
                    logging.info(f"Adding to big pit")
                    self.players[user_id].big_pit += 1
                    remaining_stones -= 1
                    if remaining_stones > 0:
                        logging.info(f"Adding to other player's pits")
                        remaining_stones = self.players[1 - user_id].add_stones(remaining_stones)
                        # Don't steal stones if we're landing on empty on the other player's pits
                        if remaining_stones == -1:
                            remaining_stones = 0
                        current_pit = 0
                    else:
                        turn -= 1
                else:
                    logging.info(f"Adding more to own pits")
                    remaining_stones = self.players[user_id].add_stones(remaining_stones)
            turn += 1
        return self.check_win(), turn % 2
