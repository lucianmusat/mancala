
class Player:

    def __init__(self, player_id: int):
        self.id = player_id
        assert self.id in [1, 2], "Must be either player 1 or 2!"
        self.big_pit = 0
        self.pits = [6] * 6
