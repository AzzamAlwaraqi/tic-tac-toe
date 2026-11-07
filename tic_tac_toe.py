import random
import tkinter as tk
from tkinter import messagebox

import pandas as pd


# Every way to get three in a row: 3 rows, 3 columns, 2 diagonals
WINNING_LINES = (
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
)

BACKGROUND = "lightblue"
X_COLOUR = "lightgreen"
O_COLOUR = "lightpink"
WIN_COLOUR = "gold"


def new_board():
    return [[None] * 3 for _ in range(3)]


def find_winner(board):
    """Return (player, line) if someone has three in a row, otherwise (None, None)."""
    for line in WINNING_LINES:
        first = board[line[0][0]][line[0][1]]
        if first is not None and all(board[r][c] == first for r, c in line):
            return first, line
    return None, None


def empty_cells(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]


def is_board_full(board):
    return not empty_cells(board)


def pick_computer_move(board, rng=random):
    """The computer just picks any free square at random."""
    free = empty_cells(board)
    return rng.choice(free) if free else None


class TicTacToe:
    def __init__(self, window=None):
        self.window = window or tk.Tk()
        self.window.title("Tic Tac Toe")
        self.window.configure(bg=BACKGROUND)
        self.window.minsize(360, 420)
        self.window.bind("<Configure>", self.resize_buttons)

        self.board = new_board()
        self.current_player = "X"
        self.game_mode = None  # "friend" or "computer"
        self.game_over = False
        self.game_number = 0
        self.results = []  # one dict per finished game, turned into a DataFrame when needed
        self.buttons = []
        self.turn_label = None

        self.create_menu()

    # ---------- screens ----------

    def create_menu(self):
        self.clear_window()

        menu = tk.Frame(self.window, bg=BACKGROUND)
        menu.pack(pady=50)

        tk.Label(menu, text="Tic Tac Toe", font=("Arial", 24, "bold"),
                 bg=BACKGROUND, fg="darkblue").pack(pady=10)

        tk.Button(menu, text="Play Against a Friend", font=("Arial", 16), bg=X_COLOUR,
                  command=lambda: self.start_game("friend")).pack(pady=5, fill="x")
        tk.Button(menu, text="Play Against Computer", font=("Arial", 16), bg=X_COLOUR,
                  command=lambda: self.start_game("computer")).pack(pady=5, fill="x")
        tk.Button(menu, text="View Scoreboard", font=("Arial", 16), bg="lightcoral",
                  command=self.show_scoreboard).pack(pady=5, fill="x")
        tk.Button(menu, text="Exit", font=("Arial", 16), bg="gray", fg="white",
                  command=self.window.destroy).pack(pady=5, fill="x")

    def start_game(self, mode):
        self.game_mode = mode
        self.current_player = "X"
        self.board = new_board()
        self.game_over = False
        self.game_number += 1
        self.create_board()

    def create_board(self):
        self.clear_window()

        board_frame = tk.Frame(self.window, bg=BACKGROUND)
        board_frame.pack(expand=True, fill="both", padx=10, pady=10)

        for row in range(3):
            button_row = []
            for col in range(3):
                button = tk.Button(board_frame, text="", font=("Arial", 32), bg="white",
                                   command=lambda r=row, c=col: self.make_move(r, c))
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                button_row.append(button)
            self.buttons.append(button_row)

        for i in range(3):
            board_frame.grid_rowconfigure(i, weight=1, uniform="cell")
            board_frame.grid_columnconfigure(i, weight=1, uniform="cell")

        self.turn_label = tk.Label(self.window, font=("Arial", 16), bg=BACKGROUND, fg="darkblue")
        self.turn_label.pack(pady=10)
        self.update_turn_label()

        tk.Button(self.window, text="Back to Menu", font=("Arial", 12), bg="lightcoral",
                  command=self.create_menu).pack(pady=10)

    def show_scoreboard(self):
        self.clear_window()

        frame = tk.Frame(self.window, bg=BACKGROUND)
        frame.pack(pady=20)

        tk.Label(frame, text="Scoreboard", font=("Arial", 24, "bold"),
                 bg=BACKGROUND, fg="darkblue").pack(pady=10)

        results = self.results_table()
        if results.empty:
            tk.Label(frame, text="No games played yet.", font=("Arial", 16),
                     bg=BACKGROUND).pack(pady=10)
        else:
            totals = results["Winner"].value_counts()
            summary = "   ".join(f"{name}: {totals.get(name, 0)}"
                                 for name in ("X", "O", "Draw"))
            tk.Label(frame, text=summary, font=("Arial", 14, "bold"),
                     bg=BACKGROUND).pack(pady=(0, 10))

            # Only the last 10 games, so the window doesn't grow forever
            for idx, row in results.tail(10).iterrows():
                text = f"Game {idx + 1}: {row['Player X']} vs {row['Player O']} - Winner: {row['Winner']}"
                tk.Label(frame, text=text, font=("Arial", 12), bg=BACKGROUND).pack(pady=2)

        tk.Button(self.window, text="Back to Menu", font=("Arial", 12), bg="lightcoral",
                  command=self.create_menu).pack(pady=10)

    # ---------- game logic ----------

    def make_move(self, row, col):
        if self.game_over or self.board[row][col] is not None:
            return

        self.place(row, col)

        if not self.game_over and self.game_mode == "computer" and self.current_player == "O":
            # Short pause so the computer's move doesn't look instant
            self.window.after(350, self.computer_move, self.game_number)

    def computer_move(self, game_number=None):
        # Skip if the player left or restarted while the computer was "thinking"
        if game_number not in (None, self.game_number):
            return
        if self.game_over or not self.buttons or self.current_player != "O":
            return
        move = pick_computer_move(self.board)
        if move:
            self.place(*move)

    def place(self, row, col):
        player = self.current_player
        self.board[row][col] = player
        self.buttons[row][col].config(text=player, bg=X_COLOUR if player == "X" else O_COLOUR,
                                      state="disabled", disabledforeground="black")

        winner, line = find_winner(self.board)
        if winner:
            for r, c in line:
                self.buttons[r][c].config(bg=WIN_COLOUR)
            self.end_game(winner)
        elif is_board_full(self.board):
            self.end_game("Draw")
        else:
            self.switch_player()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_turn_label()

    def update_turn_label(self):
        if self.game_mode == "computer":
            text = "Your turn (X)" if self.current_player == "X" else "Computer is thinking..."
        else:
            text = f"Player {self.current_player}'s turn"
        self.turn_label.config(text=text)

    def end_game(self, winner):
        self.game_over = True

        if winner == "Draw":
            message = "It's a draw!"
        elif self.game_mode == "computer":
            message = "You win!" if winner == "X" else "Computer wins!"
        else:
            message = f"Player {winner} wins!"

        against_friend = self.game_mode == "friend"
        self.results.append({
            "Player X": "Player 1" if against_friend else "You",
            "Player O": "Player 2" if against_friend else "Computer",
            "Winner": winner,
        })

        self.turn_label.config(text=message)
        # Let the final board draw before the popup appears
        self.window.after(100, self.show_result, message, self.game_number)

    def show_result(self, message, game_number):
        if game_number != self.game_number or not self.buttons:
            return  # the player already left this game
        messagebox.showinfo("Game Over", message, parent=self.window)
        self.create_menu()

    def results_table(self):
        return pd.DataFrame(self.results, columns=["Player X", "Player O", "Winner"])

    # ---------- helpers ----------

    def clear_window(self):
        # Forget the old board first, otherwise resize_buttons touches destroyed widgets
        self.buttons = []
        self.turn_label = None
        for widget in self.window.winfo_children():
            widget.destroy()

    def resize_buttons(self, event=None):
        if not self.buttons:
            return
        size = min(self.window.winfo_width(), self.window.winfo_height() - 120) // 3
        font_size = max(16, size // 3)
        for row in self.buttons:
            for button in row:
                button.config(font=("Arial", font_size, "bold"))

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    TicTacToe().run()
