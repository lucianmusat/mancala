import pytest

from board import Board, NO_WINNER
from human_player import HumanPlayer


class TestGame:

    @pytest.fixture(scope='function')
    def basic_setup(self):
        board = Board(nr_players=2)
        players = {
            0: HumanPlayer(0, board),
            1: HumanPlayer(1, board)
        }
        return board, players

    def test_game_basic_move(self, basic_setup):
        board, players = basic_setup
        players[0].select_pit(0)
        assert not players[0].move()  # We get to move again
        assert board.players_data[0].pits == [0, 7, 7, 7, 7, 7]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0

    def test_game_move_last(self, basic_setup):
        board, players = basic_setup
        players[0].select_pit(5)
        assert players[0].move()
        assert board.players_data[0].pits == [6, 6, 6, 6, 6, 0]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [7, 7, 7, 7, 7, 6]
        assert board.players_data[1].big_pit == 0

    def test_game_move_empty_pit(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [0, 7, 7, 7, 7, 7]
        board.players_data[0].big_pit = 1
        board.players_data[1].pits = [6, 6, 6, 6, 6, 6]
        board.players_data[1].big_pit = 0
        players[0].select_pit(0)
        assert not players[0].move()

    def test_game_dont_select_pit(self, basic_setup):
        board, players = basic_setup
        with pytest.raises(AssertionError):
            players[0].move()

    def test_game_move_twice(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [0, 7, 7, 7, 7, 7]
        board.players_data[0].big_pit = 1
        board.players_data[1].pits = [6, 6, 6, 6, 6, 6]
        board.players_data[1].big_pit = 0
        players[0].select_pit(1)
        assert players[0].move()
        assert board.players_data[0].pits == [0, 0, 8, 8, 8, 8]
        assert board.players_data[0].big_pit == 2
        assert board.players_data[1].pits == [7, 7, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0

    def test_game_land_on_empty(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [1, 0, 8, 8, 8, 8]
        board.players_data[0].big_pit = 2
        board.players_data[1].pits = [0, 8, 7, 7, 7, 7]
        board.players_data[1].big_pit = 1
        players[0].select_pit(0)
        assert players[0].move()
        assert board.players_data[0].pits == [0, 0, 8, 8, 8, 8]
        assert board.players_data[0].big_pit == 10
        assert board.players_data[1].pits == [0, 8, 7, 7, 0, 7]
        assert board.players_data[1].big_pit == 1

    def test_land_on_empty_with_moves(self, basic_setup):
        board, players = basic_setup
        players[0].select_pit(0)
        assert not players[0].move()
        players[0].select_pit(1)
        assert players[0].move()
        assert board.players_data[0].pits == [0, 0, 8, 8, 8, 8]
        assert board.players_data[0].big_pit == 2
        assert board.players_data[1].pits == [7, 7, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0
        players[1].select_pit(0)
        assert players[1].move()
        assert board.players_data[0].pits == [1, 0, 8, 8, 8, 8]
        assert board.players_data[0].big_pit == 2
        assert board.players_data[1].pits == [0, 8, 7, 7, 7, 7]
        assert board.players_data[1].big_pit == 1
        players[0].select_pit(0)
        assert players[0].move()
        assert board.players_data[0].pits == [0, 0, 8, 8, 8, 8]
        assert board.players_data[0].big_pit == 10
        assert board.players_data[1].pits == [0, 8, 7, 7, 0, 7]
        assert board.players_data[1].big_pit == 1

    def test_overflow_player1(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [2, 3, 9, 9, 2, 4]
        board.players_data[0].big_pit = 6
        board.players_data[1].pits = [2, 9, 8, 8, 8, 0]
        board.players_data[1].big_pit = 2
        players[0].select_pit(5)
        assert players[0].move()
        assert board.players_data[0].pits == [2, 3, 9, 9, 2, 0]
        assert board.players_data[0].big_pit == 7
        assert board.players_data[1].pits == [3, 10, 9, 8, 8, 0]
        assert board.players_data[1].big_pit == 2

    def test_overflow_player1_back_around(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [2, 1, 9, 9, 1, 10]
        board.players_data[0].big_pit = 3
        board.players_data[1].pits = [2, 9, 8, 8, 8, 0]
        board.players_data[1].big_pit = 2
        players[0].select_pit(5)
        assert players[0].move()
        assert board.players_data[0].pits == [3, 2, 10, 9, 1, 0]
        assert board.players_data[0].big_pit == 4
        assert board.players_data[1].pits == [3, 10, 9, 9, 9, 1]
        assert board.players_data[1].big_pit == 2

    def test_overflow_player2(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [0, 7, 7, 7, 7, 7]
        board.players_data[0].big_pit = 1
        board.players_data[1].pits = [6, 6, 6, 6, 6, 3]
        board.players_data[1].big_pit = 3
        players[1].select_pit(5)
        assert players[1].move()
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 0]
        assert board.players_data[1].big_pit == 4
        assert board.players_data[0].pits == [1, 8, 7, 7, 7, 7]
        assert board.players_data[0].big_pit == 1

    def test_land_in_big_pit(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [6, 6, 4, 6, 6, 6]
        board.players_data[0].big_pit = 2
        board.players_data[1].pits = [6, 6, 6, 6, 6, 6]
        board.players_data[1].big_pit = 0
        players[0].select_pit(2)
        assert not players[0].move()
        assert board.players_data[0].pits == [6, 6, 0, 7, 7, 7]
        assert board.players_data[0].big_pit == 3
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0

    def test_player_move(self, basic_setup):
        board, players = basic_setup
        assert board.players_data[0].big_pit == board.players_data[1].big_pit == 0
        assert board.players_data[0].pits == board.players_data[0].pits == [6, 6, 6, 6, 6, 6]
        players[0].select_pit(0)
        assert not players[0].move()
        assert board.players_data[0].pits == [0, 7, 7, 7, 7, 7]

    def test_player_move_twice(self, basic_setup):
        board, players = basic_setup
        players[0].select_pit(5)
        assert players[0].move()
        assert board.players_data[0].pits == [6, 6, 6, 6, 6, 0]
        board.players_data[0].pits = [6, 2, 6, 6, 6, 0]
        players[0].select_pit(1)
        assert players[0].move()
        assert board.players_data[0].pits == [6, 0, 7, 7, 6, 0]

    def test_player_collect_all_stones(self, basic_setup):
        board, players = basic_setup
        board.players_data[0].pits = [9, 9, 9, 8, 8, 8]
        board.collect_all_stones(0)
        assert board.players_data[0].pits == [0, 0, 0, 0, 0, 0]
        assert board.players_data[0].big_pit == 51

    def test_game_win(self, basic_setup):
        board, players = basic_setup
        assert board.winner == NO_WINNER
        board.players_data[0].pits = [0, 0, 0, 0, 0, 0]
        board.players_data[1].pits = [12, 12, 12, 12, 12, 12]
        board.collect_all_stones(1)
        assert board.winner == 1
        board.reset()
        board.players_data[0].pits = [12, 12, 12, 12, 12, 12]
        board.players_data[1].pits = [0, 0, 0, 0, 0, 0]
        board.collect_all_stones(0)
        assert board.winner == 0
