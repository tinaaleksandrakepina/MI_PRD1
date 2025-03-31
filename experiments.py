import time
import random
import statistics
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

class Experiment:
    def __init__(self):
        self.nodes_visited = 0

    def evaluate_state(self, state: GameState):
        score_diff = state.computer_score - state.player_score
        closeness = state.current_number / TARGET
        return score_diff + closeness

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

    def run_experiments(self, algorithm_name: str):
        results = []
        times = []
        all_nodes = []

        for i in range(10):
            current = random.randint(8, 18)
            print(f"\n{i+1}. spēle sākas ar skaitli: {current}")
            player_score = 0
            computer_score = 0
            bank = 0
            turn = False  # DATORS sāk

            while current < TARGET:
                state = GameState(current, player_score, computer_score, bank, turn)
                self.nodes_visited = 0
                start = time.perf_counter()

                if algorithm_name == "minimax":
                    _, move = self.minimax(state, True, 3)
                else:
                    _, move = self.alpha_beta(state, True, 3, float("-inf"), float("inf"))

                end = time.perf_counter()
                move_time = end - start
                times.append(move_time)
                all_nodes.append(self.nodes_visited)
                print(f"  Dators izvēlas x{move}, ilgums: {move_time:.6f}s, apmeklētās virsotnes: {self.nodes_visited}")

                current *= move
                bank_points = 1 if current % 10 in [0, 5] else 0
                score_change = 1 if current % 2 else -1

                if turn:
                    player_score += score_change
                else:
                    computer_score += score_change
                bank += bank_points

                if current >= TARGET:
                    if turn:
                        player_score += bank
                    else:
                        computer_score += bank
                    bank = 0
                    break

                turn = not turn

            if player_score > computer_score:
                results.append("Cilvēks")
            elif computer_score > player_score:
                results.append("Dators")
            else:
                results.append("Neizšķirts")

        print(f"\n--- Kopsavilkums ({algorithm_name}) ---")
        print("Datora uzvaras:", results.count("Dators"))
        print("Cilvēka uzvaras:", results.count("Cilvēks"))
        print("Neizšķirti:", results.count("Neizšķirts"))
        print(f"Vidēji apmeklētās virsotnes: {statistics.mean(all_nodes):.2f}")
        print(f"Vidējais gājiena ilgums: {statistics.mean(times):.6f} sekundes")

if __name__ == "__main__":
    exp = Experiment()
    print("Notiek Minimax algoritma eksperimenti:")
    exp.run_experiments("minimax")

    print("\nNotiek Alpha-Beta algoritma eksperimenti:")
    exp.run_experiments("alpha-beta")
