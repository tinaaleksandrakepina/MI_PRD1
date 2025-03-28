import tkinter as tk
from tkinter import messagebox
import time
from dataclasses import dataclass, field
from typing import List, Optional

TARGET = 1200
MULTIPLIERS = [2, 3, 4]

@dataclass
class GameState:
    current_number: int
    player_score: int
    computer_score: int
    bank: int
    is_player_turn: bool  # True = Human, False = Computer
    move: Optional[int] = None
    parent: Optional["GameState"] = None
    children: List["GameState"] = field(default_factory=list)
    depth: int = 0

    def is_terminal(self):
        return self.current_number >= TARGET

    def generate_children(self):
        if self.is_terminal():
            return

        for factor in MULTIPLIERS:
            new_number = self.current_number * factor
            player_pts = self.player_score
            comp_pts = self.computer_score
            bank_val = self.bank

            score_change = 1 if new_number % 2 else -1
            bank_bonus = 1 if new_number % 10 in [0, 5] else 0

            if self.is_player_turn:
                player_pts += score_change
            else:
                comp_pts += score_change

            bank_val += bank_bonus

            if new_number >= TARGET:
                if self.is_player_turn:
                    player_pts += bank_val
                else:
                    comp_pts += bank_val
                bank_val = 0

            next_turn = self.is_player_turn if new_number >= TARGET else not self.is_player_turn

            child = GameState(
                current_number=new_number,
                player_score=player_pts,
                computer_score=comp_pts,
                bank=bank_val,
                is_player_turn=next_turn,
                move=factor,
                parent=self,
                depth=self.depth + 1
            )

            self.children.append(child)

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Game: Minimax vs Alpha-Beta")

        self.setup_ui()
        self.algorithm = None
        self.current_number = None
        self.player_score = 0
        self.computer_score = 0
        self.bank = 0
        self.player_turn = True

    def setup_ui(self):
        tk.Label(self.root, text="Select who starts:").pack()
        self.turn_var = tk.StringVar(value="human")
        tk.Radiobutton(self.root, text="Human", variable=self.turn_var, value="human").pack()
        tk.Radiobutton(self.root, text="Computer", variable=self.turn_var, value="computer").pack()

        tk.Label(self.root, text="Select algorithm:").pack()
        self.algo_var = tk.StringVar(value="minimax")
        tk.Radiobutton(self.root, text="Minimax", variable=self.algo_var, value="minimax").pack()
        tk.Radiobutton(self.root, text="Alpha-Beta", variable=self.algo_var, value="alpha-beta").pack()

        tk.Label(self.root, text="Enter seed number (8-18):").pack()
        self.entry = tk.Entry(self.root)
        self.entry.pack()

        self.start_button = tk.Button(self.root, text="Start game", command=self.start_game, fg="black")
        self.start_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.computer_msg = tk.Label(self.root, text="")
        self.computer_msg.pack()

        self.move_buttons = []
        for m in MULTIPLIERS:
            btn = tk.Button(self.root, text=f"x{m}", command=lambda m=m: self.player_move(m), fg="black")
            btn.pack()
            btn.config(state=tk.DISABLED)
            self.move_buttons.append(btn)

        self.restart_button = tk.Button(self.root, text="Restart Game", command=self.restart_game, fg="black")
        self.restart_button.pack()
        self.restart_button.config(state=tk.DISABLED)

    def start_game(self):
        try:
            num = int(self.entry.get())
            if num < 8 or num > 18:
                raise ValueError
        except ValueError:
            messagebox.showerror("error", "Enter a number between 8 and 18")
            return

        self.current_number = num
        self.algorithm = self.algo_var.get()
        self.player_turn = (self.turn_var.get() == "human")
        self.entry.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.update_status()
        self.computer_msg.config(text="")

        if self.player_turn:
            self.enable_buttons()
        else:
            self.disable_buttons()
            self.root.after(1000, self.computer_move)

    def enable_buttons(self):
        for btn in self.move_buttons:
            btn.config(state=tk.NORMAL)

    def disable_buttons(self):
        for btn in self.move_buttons:
            btn.config(state=tk.DISABLED)

    def player_move(self, multiplier):
        if not self.player_turn:
            return

        self.make_move(multiplier, player=True)
        self.computer_msg.config(text="")

        if self.current_number >= TARGET:
            self.end_game()
            return

        self.player_turn = False
        self.disable_buttons()
        self.root.after(1000, self.computer_move)

    def computer_move(self):
        self.computer_msg.config(text="Computer is thinking...")
        self.root.update()
        time.sleep(1)  # <-- Pause for 1 second

        state = GameState(
            current_number=self.current_number,
            player_score=self.player_score,
            computer_score=self.computer_score,
            bank=self.bank,
            is_player_turn=False
        )

        if self.algorithm == "minimax":
            best_move = self.minimax(state, True, 3)[1]
        else:
            best_move = self.alpha_beta(state, True, 3, float("-inf"), float("inf"))[1]

        self.make_move(best_move, player=False)
        self.computer_msg.config(text=f"Computer chose x{best_move}")

        if self.current_number >= TARGET:
            self.end_game()
            return

        self.player_turn = True
        self.enable_buttons()

    def make_move(self, multiplier, player):
        self.current_number *= multiplier
        points = 1 if self.current_number % 2 else -1
        bank_points = 1 if self.current_number % 10 in [0, 5] else 0

        if player:
            self.player_score += points
        else:
            self.computer_score += points

        self.bank += bank_points
        self.update_status()

    def update_status(self):
        self.status_label.config(
            text=f"Number: {self.current_number}\nPlayer: {self.player_score}, Computer: {self.computer_score}\nBank: {self.bank}"
        )

    def evaluate_state(self, state: GameState):
        score_diff = state.computer_score - state.player_score
        closeness = state.current_number / TARGET
        return score_diff + closeness

    def minimax(self, state: GameState, maximizing: bool, depth: int):
        if state.is_terminal() or depth == 0:
            return self.evaluate_state(state), None

        state.generate_children()
        best_move = None

        if maximizing:
            max_eval = float("-inf")
            for child in state.children:
                eval, _ = self.minimax(child, False, depth - 1)
                if eval > max_eval:
                    max_eval = eval
                    best_move = child.move
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for child in state.children:
                eval, _ = self.minimax(child, True, depth - 1)
                if eval < min_eval:
                    min_eval = eval
                    best_move = child.move
            return min_eval, best_move

    def alpha_beta(self, state: GameState, maximizing: bool, depth: int, alpha: float, beta: float):
        if state.is_terminal() or depth == 0:
            return self.evaluate_state(state), None

        state.generate_children()
        best_move = None

        if maximizing:
            max_eval = float("-inf")
            for child in state.children:
                eval, _ = self.alpha_beta(child, False, depth - 1, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = child.move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for child in state.children:
                eval, _ = self.alpha_beta(child, True, depth - 1, alpha, beta)
                if eval < min_eval:
                    min_eval = eval
                    best_move = child.move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def end_game(self):
        if self.player_turn:
            self.player_score += self.bank
        else:
            self.computer_score += self.bank

        self.disable_buttons()
        self.status_label.config(
            text=f"Game Over!\nFinal Score: Player {self.player_score} - {self.computer_score} Computer\nBank: {self.bank}"
        )
        self.computer_msg.config(text="")
        self.restart_button.config(state=tk.NORMAL)

    def restart_game(self):
        self.player_score = 0
        self.computer_score = 0
        self.bank = 0
        self.current_number = None
        self.status_label.config(text="")
        self.computer_msg.config(text="")

        self.entry.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.DISABLED)

        self.enable_buttons()
        for btn in self.move_buttons:
            btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
