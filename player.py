from abc import ABC


class Player(ABC):

    def __init__(self, player_id: int):
        self.id = player_id
        assert self.id in [1, 2], "Must be either player 1 or 2!"
        self.big_pit = 0
        self.pits = [6] * 6

    def legal_move(self, pit: int) -> bool:
        if pit not in range(0, 6):
            input(f"Illegal move, {pit} must be in range 1..6!")
            return False
        if self.pits[pit] == 0:
            input(f"The pit {pit} does not contain any stones!")
            return False
        return True

    def move(self, other_player) -> bool:
        raise NotImplementedError


class HumanPlayer(Player):
    def move(self, other_player) -> bool:
        # Game logic
        pit = int(input(f"Player {self.id} move [1-6]: ")) - 1
        if not self.legal_move(pit):
            return False

        available_stones = self.pits[pit]
        assert available_stones > 0, "No stones to pick!"
        self.pits[pit] = 0
        # Put stones in the next pits
        while available_stones > 0:
            for i in range(pit + 1, 6):
                if available_stones > 0:
                    print(f"Adding stone to pit {i}. Available stones: {available_stones}")
                    self.pits[i] += 1
                    available_stones -= 1
            # If we have stones still in the hand put it in the big pit
            if available_stones > 0:
                print(f"Adding a stone to the big pit. Available stones: {available_stones}")
                self.big_pit += 1
                available_stones -= 1
            # If we still have stones in the hand start putting in player2 pits
            if available_stones > 0:
                for i in range(0, 6):
                    print(f"Available stones: {available_stones}. Adding a stone to the other player's pit {i}")
                    other_player.pits[i] += 1
                    available_stones -= 1
            # Still have stones, need to start from the beginning
            if available_stones > 0:
                print(f"Still have stones left: {available_stones}, starting over")
                pit = -1
        return True
