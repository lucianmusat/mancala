from player import Player


class Board:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        assert self.player1.id != self.player2.id, f"Cannot have two player{self.player1.id}!"

    def player_move(self, player: Player, pit: int):
        # Game logic
        other_player = self.player2 if player.id == 1 else self.player1
        available_stones = player.pits[pit]
        assert available_stones > 0, "No stones to pick!"
        player.pits[pit] = 0
        # Put stones in the next pits
        while available_stones > 0:
            for i in range(pit + 1, 6):
                if available_stones > 0:
                    print(f"Adding stone to pit {i}. Available stones: {available_stones}")
                    player.pits[i] += 1
                    available_stones -= 1
            # If we have stones still in the hand put it in the big pit
            if available_stones > 0:
                print(f"Adding a stone to the big pit. Available stones: {available_stones}")
                player.big_pit += 1
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

    def move(self, player_id: int, pit: int):
        if player_id == 1:
            self.player_move(self.player1, pit)
        else:
            self.player_move(self.player2, pit)
