from board import Board, NO_WINNER


class TestBoard:

    def test_board_init(self):
        board = Board(nr_players=2)
        assert board.nr_players == 2
        assert board.players_data[0].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[0].big_pit == 0
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0
        assert board.winner == NO_WINNER

    def test_board_move(self):
        board = Board(nr_players=2)
        board.move(0, 0)
        assert board.players_data[0].pits == [0, 7, 7, 7, 7, 7]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0
        assert board.winner == NO_WINNER

    def test_board_move_last(self):
        board = Board(nr_players=2)
        board.move(0, 5)
        assert board.players_data[0].pits == [6, 6, 6, 6, 6, 0]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [7, 7, 7, 7, 7, 6]
        assert board.players_data[1].big_pit == 0
        assert board.winner == NO_WINNER

    def test_board_move_empty_pit(self):
        board = Board(nr_players=2)
        board.players_data[0].pits = [0, 7, 7, 7, 7, 7]
        board.players_data[0].big_pit = 1
        board.players_data[1].pits = [6, 6, 6, 6, 6, 6]
        board.players_data[1].big_pit = 0
        board.move(0, 0)
        assert board.players_data[0].pits == [0, 7, 7, 7, 7, 7]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [6, 6, 6, 6, 6, 6]
        assert board.players_data[1].big_pit == 0
        assert board.winner == NO_WINNER

    def test_board_move_last_empty_pit(self):
        board = Board(nr_players=2)
        board.players_data[0].pits = [6, 6, 6, 6, 6, 0]
        board.players_data[0].big_pit = 1
        board.players_data[1].pits = [7, 7, 7, 7, 7, 6]
        board.players_data[1].big_pit = 0
        board.move(0, 5)
        assert board.players_data[0].pits == [6, 6, 6, 6, 6, 0]
        assert board.players_data[0].big_pit == 1
        assert board.players_data[1].pits == [7, 7, 7, 7, 7, 6]
        assert board.players_data[1].big_pit == 0
        assert board.winner == NO_WINNER

    def test_board_winner(self):
        board = Board(nr_players=2)
        board.players_data[0].pits = [0, 0, 0, 0, 0, 0]
        board.players_data[0].big_pit = 38
        board.players_data[1].pits = [0, 0, 0, 0, 0, 0]
        board.players_data[1].big_pit = 34
        assert board.winner == 0

    def test_board_move_win(self):
        board = Board(nr_players=2)
        board.players_data[0].pits = [0, 0, 0, 0, 0, 1]
        board.players_data[0].big_pit = 37
        board.players_data[1].pits = [0, 0, 0, 0, 0, 0]
        board.players_data[1].big_pit = 34
        board.move(0, 5)
        assert board.players_data[0].pits == [0, 0, 0, 0, 0, 0]
        assert board.players_data[0].big_pit == 38
        assert board.players_data[1].pits == [0, 0, 0, 0, 0, 0]
        assert board.players_data[1].big_pit == 34
        assert board.winner == 0
