from typing import List


class Board:

    def __init__(self):
        self.player_one_big_pit = 0
        self.player_two_big_pit = 0
        self.player_one_pits = [6] * 6
        self.player_two_pits = [6] * 6

    def player_big_pit(self, player_id: int) -> int:
        if player_id == 1:
            return self.player_one_big_pit
        else:
            return self.player_two_big_pit

    def player_pits(self, player_id: int) -> List[int]:
        if player_id == 1:
            return self.player_one_pits
        else:
            return self.player_two_pits

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        if player_id == 1:
            self.player_one_big_pit += stones
        else:
            self.player_two_big_pit += stones

    def add_stones_to_pit(self, player_id: int, index: int, stones: int) -> None:
        if player_id == 1:
            self.player_one_pits[index] += stones
        else:
            self.player_two_pits[index] += stones

    def increment_pit(self, player_id: int, index: int) -> None:
        self.add_stones_to_pit(player_id, index, 1)

    def increment_big_pit(self, player_id: int) -> None:
        self.add_stones_to_big_pit(player_id, 1)

    def reset_pit(self, player_id: int, index: int) -> None:
        if player_id == 1:
            self.player_one_pits[index] = 0
        else:
            self.player_two_pits[index] = 0

    def reset_all_pits(self, player_id: int) -> None:
        if player_id == 1:
            self.player_one_pits = [0] * 6
        else:
            self.player_two_pits = [0] * 6
