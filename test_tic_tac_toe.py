import random
import tkinter as tk
import unittest
from unittest import mock

import tic_tac_toe as ttt


def board_from(rows):
    """Build a board from strings like 'XO.', where '.' is an empty square."""
    return [[None if ch == "." else ch for ch in row] for row in rows]


class BoardLogicTests(unittest.TestCase):
    def test_empty_board_has_no_winner(self):
        self.assertEqual(ttt.find_winner(ttt.new_board()), (None, None))

    def test_finds_every_winning_line(self):
        for line in ttt.WINNING_LINES:
            for player in ("X", "O"):
                board = ttt.new_board()
                for r, c in line:
                    board[r][c] = player
                self.assertEqual(ttt.find_winner(board), (player, line))

    def test_finds_winner_regardless_of_whose_turn_it_is(self):
        # The old version only checked the current player, so this was missed
        board = board_from(["OOO", "XX.", "X.."])
        self.assertEqual(ttt.find_winner(board)[0], "O")

    def test_full_board_without_line_is_a_draw(self):
        board = board_from(["XOX", "XOO", "OXX"])
        self.assertEqual(ttt.find_winner(board), (None, None))
        self.assertTrue(ttt.is_board_full(board))

    def test_computer_only_picks_free_squares(self):
        board = board_from(["XO.", "OX.", "..X"])
        free = set(ttt.empty_cells(board))
        rng = random.Random(1)
        for _ in range(50):
            self.assertIn(ttt.pick_computer_move(board, rng), free)

    def test_computer_has_no_move_on_full_board(self):
        self.assertIsNone(ttt.pick_computer_move(board_from(["XOX", "XOO", "OXX"])))


class GameWindowTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.popup = mock.patch.object(ttt.messagebox, "showinfo").start()
        self.game = ttt.TicTacToe(self.root)

    def tearDown(self):
        mock.patch.stopall()
        self.root.destroy()

    def settle(self):
        """Run pending after() callbacks, like the computer's delayed move."""
        self.root.after(500, self.root.quit)
        self.root.mainloop()

    def test_friend_game_x_wins_and_is_recorded(self):
        self.game.start_game("friend")
        for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            self.game.make_move(*move)
        self.settle()

        self.popup.assert_called_once()
        self.assertIn("Player X wins!", self.popup.call_args[0])
        results = self.game.results_table()
        self.assertEqual(list(results["Winner"]), ["X"])

    def test_clicking_taken_square_does_nothing(self):
        self.game.start_game("friend")
        self.game.make_move(1, 1)
        self.game.make_move(1, 1)
        self.assertEqual(self.game.board[1][1], "X")
        self.assertEqual(self.game.current_player, "O")

    def test_no_moves_after_game_ends(self):
        self.game.start_game("friend")
        for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            self.game.make_move(*move)
        self.game.make_move(2, 2)
        self.assertIsNone(self.game.board[2][2])

    def test_draw_is_recorded(self):
        self.game.start_game("friend")
        for move in [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)]:
            self.game.make_move(*move)
        self.settle()
        self.assertEqual(list(self.game.results_table()["Winner"]), ["Draw"])

    def test_computer_answers_after_player_moves(self):
        self.game.start_game("computer")
        self.game.make_move(1, 1)
        self.assertEqual(self.game.current_player, "O")
        self.settle()
        self.assertEqual(sum(cell == "O" for row in self.game.board for cell in row), 1)
        self.assertEqual(self.game.current_player, "X")

    def test_computer_does_not_move_into_a_new_game(self):
        self.game.start_game("computer")
        self.game.make_move(0, 0)
        self.game.start_game("computer")  # restart before the computer replies
        self.settle()
        self.assertEqual(self.game.board, ttt.new_board())

    def test_resizing_after_returning_to_menu_does_not_crash(self):
        # Used to raise TclError: resize touched buttons that were already destroyed
        self.game.start_game("friend")
        self.game.create_menu()
        self.game.resize_buttons()
        self.root.event_generate("<Configure>")

    def test_scoreboard_shows_totals(self):
        self.game.results = [
            {"Player X": "You", "Player O": "Computer", "Winner": "X"},
            {"Player X": "You", "Player O": "Computer", "Winner": "Draw"},
        ]
        self.game.show_scoreboard()
        texts = [w.cget("text") for f in self.root.winfo_children()
                 for w in f.winfo_children() if isinstance(w, tk.Label)]
        self.assertIn("X: 1   O: 0   Draw: 1", texts)


if __name__ == "__main__":
    unittest.main()
