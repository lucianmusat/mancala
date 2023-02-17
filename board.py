from typing import List

from utils import MoveResult


class Board:

    def __init__(self):
        self.player_one_big_pit = 0
        self.player_two_big_pit = 0
        self.player_one_pits = [6] * 6
        self.player_two_pits = [6] * 6

    def player_big_pit(self, player_id: int) -> int:
        if player_id == 1:
            return self.player_one_big_pit
        elif player_id == 2:
            return self.player_two_big_pit
        return -1

    def player_pits(self, player_id: int) -> List[int]:
        if player_id == 1:
            return self.player_one_pits
        elif player_id == 2:
            return self.player_two_pits
        return []

    def add_stones_to_big_pit(self, player_id: int, stones: int) -> None:
        if stones > 0:
            if player_id == 1:
                self.player_one_big_pit += stones
            elif player_id == 2:
                self.player_two_big_pit += stones

    def add_stones_to_pit(self, player_id: int, index: int, stones: int) -> None:
        if stones > 0:
            if player_id == 1:
                self.player_one_pits[index] += stones
            elif player_id == 2:
                self.player_two_pits[index] += stones

    def increment_pit(self, player_id: int, index: int) -> None:
        self.add_stones_to_pit(player_id, index, 1)

    def increment_big_pit(self, player_id: int) -> None:
        self.add_stones_to_big_pit(player_id, 1)

    def reset_pit(self, player_id: int, index: int) -> None:
        if player_id == 1:
            self.player_one_pits[index] = 0
        elif player_id == 2:
            self.player_two_pits[index] = 0

    def reset_all_pits(self, player_id: int) -> None:
        if player_id == 1:
            self.player_one_pits = [0] * 6
        elif player_id == 2:
            self.player_two_pits = [0] * 6

    def move_pit(self, player_id: int, pit: int) -> MoveResult:
        """
        The main game logic. Calculates how the stones will be divided
        after choosing a pit.
        :param player_id: Id of the player that moves
        :param pit: Player's pit index
        :return: If the move was valid or not, or special case when it
        landed inside its own big pit
        """
        other_player_id = 1 if player_id == 2 else 2
        available_stones = self.player_pits(player_id)[pit]
        assert available_stones > 0, "No stones to pick!"
        self.reset_pit(player_id, pit)
        # Put stones in the next pits
        while available_stones > 0:
            for i in range(pit + 1, 6):
                if available_stones > 0:
                    print(f"Adding stone to pit {i}. Available stones: {available_stones}")
                    self.increment_pit(player_id, i)
                    available_stones -= 1
                    # Landed on an empty pit
                    if available_stones == 0 and self.player_pits(player_id)[i] == 1:
                        print("Taking opponents stones")
                        self.reset_pit(player_id, i)
                        opposite_stones = self.player_pits(other_player_id)[5 - i]
                        self.reset_pit(other_player_id, 5 - i)
                        self.add_stones_to_big_pit(player_id, opposite_stones + 1)
                else:
                    break
            # If we have stones still in the hand put it in the big pit
            if available_stones > 0:
                print(f"Adding a stone to the big pit. Available stones: {available_stones}")
                self.increment_big_pit(player_id)
                available_stones -= 1
                # Last stone landed in own big pit
                if available_stones == 0:
                    return MoveResult.InOwnBigPit
            # If we still have stones in the hand start putting in player2 pits
            if available_stones > 0:
                for i in range(0, 6):
                    print(f"Available stones: {available_stones}. Adding a stone to the other player's pit {i}")
                    self.increment_pit(other_player_id, i)
                    available_stones -= 1
                    if available_stones == 0:
                        break
            # Still have stones, need to start from the beginning
            if available_stones > 0:
                print(f"Still have stones left: {available_stones}, starting over")
                pit = -1
        return MoveResult.Valid
