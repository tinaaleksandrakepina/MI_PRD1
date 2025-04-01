import customtkinter as ctk
import tkinter.messagebox as messagebox
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
    is_player_turn: bool
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

            bank_val += bank_bonus
            if self.is_player_turn:
                player_pts += score_change
            else:
                comp_pts += score_change

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

@dataclass
class GameStats:
    total_moves: int = 0
    total_time: float = 0.0
    total_nodes: int = 0

    def add(self, move_time, visited_nodes):
        self.total_moves += 1
        self.total_time += move_time
        self.total_nodes += visited_nodes

    def get_average_time(self):
        return self.total_time / self.total_moves if self.total_moves > 0 else 0

    def get_average_nodes(self):
        return self.total_nodes / self.total_moves if self.total_moves > 0 else 0

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Mākslīgā intelekta spēle")
        self.root.geometry("700x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.algorithm = None
        self.current_number = None
        self.player_score = 0
        self.computer_score = 0
        self.bank = 0
        self.player_turn = True
        self.stats = GameStats()
        self.nodes_visited = 0

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.turn_var = ctk.StringVar(value="CILVĒKS")
        self.algo_var = ctk.StringVar(value="minimax")

        ctk.CTkLabel(self.main_frame, text="Izvēlies, kurš sāk:").pack(pady=5)
        ctk.CTkSegmentedButton(self.main_frame, values=["CILVĒKS", "DATORS"], variable=self.turn_var).pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="Izvēlies algoritmu:").pack(pady=5)
        ctk.CTkSegmentedButton(self.main_frame, values=["minimax", "alpha-beta"], variable=self.algo_var).pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="Ievadi sākuma skaitli (8–18):").pack(pady=5)
        self.entry = ctk.CTkEntry(self.main_frame)
        self.entry.pack(pady=5)

        self.start_button = ctk.CTkButton(self.main_frame, text="Sākt spēli", command=self.start_game)
        self.start_button.pack(pady=5)

        rules_text = (
            "\nSpēles noteikumi:\n"
            "- Sākuma skaitlis no 8 līdz 18.\n"
            "- Katrs spēlētājs sāk ar 0 punktiem.\n"
            "- Katrs gājiens reizināts ar 2, 3 vai 4.\n"
            "- Pāra skaitļi: -1 punkts, nepāra: +1 punkts.\n"
            "- Skaitļi ar 0 vai 5 beigās -> +1 punktu bankai.\n"
            "- Kad sasniedz 1200 vai vairāk: spēle beidzas, un banka piešķirta pēdējam spēlētājam."
        )
        ctk.CTkLabel(self.main_frame, text=rules_text, justify="left", font=("Arial", 12), text_color="lightgrey", wraplength=650).pack(pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 16))
        self.status_label.pack(pady=10)

        self.computer_msg = ctk.CTkLabel(self.main_frame, text="")
        self.computer_msg.pack()

        self.move_buttons = []
        for m in MULTIPLIERS:
            btn = ctk.CTkButton(self.main_frame, text=f"x{m}", command=lambda m=m: self.player_move(m))
            btn.pack(pady=2)
            btn.configure(state="disabled")
            self.move_buttons.append(btn)

        self.restart_button = ctk.CTkButton(self.main_frame, text="Restartēt spēli", command=self.restart_game, state="disabled")
        self.restart_button.pack(pady=10)

    def start_game(self):
        try:
            num = int(self.entry.get())
            if num < 8 or num > 18:
                raise ValueError
        except ValueError:
            messagebox.showerror("Kļūda", "Ievadi skaitli no 8 līdz 18")
            return

        self.current_number = num
        self.algorithm = self.algo_var.get()
        self.player_turn = (self.turn_var.get() == "CILVĒKS")
        self.entry.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.update_status()
        self.computer_msg.configure(text="")
        self.stats = GameStats()

        if self.player_turn:
            self.enable_buttons()
        else:
            self.disable_buttons()
            self.root.after(1000, self.computer_move)

    def enable_buttons(self):
        for btn in self.move_buttons:
            btn.configure(state="normal")

    def disable_buttons(self):
        for btn in self.move_buttons:
            btn.configure(state="disabled")

    def player_move(self, multiplier):
        if not self.player_turn:
            return
        self.make_move(multiplier, player=True)
        self.computer_msg.configure(text="")

        if self.current_number >= TARGET:
            self.end_game()
            return

        self.player_turn = False
        self.disable_buttons()
        self.root.after(1000, self.computer_move)

    def computer_move(self):
        self.computer_msg.configure(text="Dators domā...")
        self.root.update()
        time.sleep(0.5)

        state = GameState(
            current_number=self.current_number,
            player_score=self.player_score,
            computer_score=self.computer_score,
            bank=self.bank,
            is_player_turn=False
        )

        self.nodes_visited = 0
        start = time.perf_counter()

        if self.algorithm == "minimax":
            move = self.minimax(state, True, 3)[1]
        else:
            move = self.alpha_beta(state, True, 3, float("-inf"), float("inf"))[1]

        duration = time.perf_counter() - start
        self.stats.add(duration, self.nodes_visited)

        self.make_move(move, player=False)
        self.computer_msg.configure(text=f"Dators izvēlējās x{move}")

        if self.current_number >= TARGET:
            self.end_game()
            return

        self.player_turn = True
        self.enable_buttons()

    def make_move(self, multiplier, player):
        new_number = self.current_number * multiplier
        bank_bonus = 1 if new_number % 10 in [0, 5] else 0
        self.bank += bank_bonus

        points = 1 if new_number % 2 else -1
        if player:
            self.player_score += points
        else:
            self.computer_score += points

        if new_number >= TARGET:
            if player:
                self.player_score += self.bank
            else:
                self.computer_score += self.bank
            self.bank = 0

        self.current_number = new_number
        self.update_status()

    def update_status(self):
        self.status_label.configure(
            text=f"Skaitlis: {self.current_number}\nCilvēks: {self.player_score}, Dators: {self.computer_score}\nBanka: {self.bank}"
        )

    def evaluate_state(self, state: GameState):
        return state.computer_score - state.player_score + state.current_number / TARGET

    def minimax(self, state: GameState, maximizing: bool, depth: int):
        self.nodes_visited += 1
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
        self.nodes_visited += 1
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
        self.disable_buttons()
        if self.player_score > self.computer_score:
            winner = "Uzvarētājs: Cilvēks 🎉"
        elif self.computer_score > self.player_score:
            winner = "Uzvarētājs: Dators 🤖"
        else:
            winner = "Rezultāts: Neizšķirts 🤝"

        stats = (
            f"{winner}\n"
            f"Spēle beigusies!\n"
            f"Rezultāts: Cilvēks {self.player_score} - {self.computer_score} Dators\n"
            f"Vid. gājiena laiks: {self.stats.get_average_time():.6f} sek\n"
            f"Vid. virsotņu skaits: {self.stats.get_average_nodes():.2f}"
        )

        self.status_label.configure(text=stats)
        self.computer_msg.configure(text="")
        self.restart_button.configure(state="normal")

    def restart_game(self):
        self.player_score = 0
        self.computer_score = 0
        self.bank = 0
        self.current_number = None
        self.stats = GameStats()
        self.status_label.configure(text="")
        self.computer_msg.configure(text="")
        self.entry.configure(state="normal")
        self.start_button.configure(state="normal")
        self.restart_button.configure(state="disabled")
        self.enable_buttons()
        for btn in self.move_buttons:
            btn.configure(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    game = Game(root)
    root.mainloop()
