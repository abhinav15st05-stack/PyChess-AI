from pieces import Pawn, Rook, Knight, Bishop, Queen, King
import math
import random

# ─── Piece Values & Tables ──────────────────────────────────────────────────
PIECE_VALUES = {
    Pawn:   100,
    Knight: 320,
    Bishop: 330,
    Rook:   500,
    Queen:  900,
    King:   20000
}

# ... [Insert your existing Piece Tables here] ...

def evaluate_board(board):
    score = 0
    for row in range(8):
        for col in range(8):
            piece = board.grid[row][col]
            if piece is None: continue
            
            piece_type = type(piece)
            value = PIECE_VALUES.get(piece_type, 0)
            
            # ... [Insert existing positional logic] ...
    return score

class ChessAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.nodes_searched = 0

    def order_moves(self, board, moves):
        """Move Ordering: Sort captures first to optimize Alpha-Beta pruning."""
        def move_score(move):
            fr_pos, to_pos = move
            target = board.grid[to_pos[0]][to_pos[1]]
            if target: 
                return PIECE_VALUES.get(type(target), 0)
            return 0
        
        return sorted(moves, key=move_score, reverse=True)

    def get_best_move(self, board):
        self.nodes_searched = 0
        best_score = -math.inf
        best_moves = []  

        all_moves = board.get_all_legal_moves('black')
        
        # Shuffle to prevent repetitive AI behavior
        random.shuffle(all_moves) 
        all_moves = self.order_moves(board, all_moves) 

        for from_pos, to_pos in all_moves:
            board.make_move(from_pos, to_pos)
            score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move()

            # Tie-breaking logic
            if score > best_score:
                best_score = score
                best_moves = [(from_pos, to_pos)] 
            elif score == best_score:
                best_moves.append((from_pos, to_pos))  

        # Pick randomly from equally good moves
        final_move = random.choice(best_moves) if best_moves else None

        print(f"[AI] Nodes: {self.nodes_searched} | Score: {best_score} | Options: {len(best_moves)}")
        return final_move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        self.nodes_searched += 1

        if depth == 0:
            return evaluate_board(board)

        color = 'black' if is_maximizing else 'white'
        all_moves = board.get_all_legal_moves(color)

        if not all_moves:
            if board.is_in_check(color):
                return math.inf if not is_maximizing else -math.inf
            return 0

        # Shuffle inside minimax for varied tree exploration
        random.shuffle(all_moves)
        all_moves = self.order_moves(board, all_moves)

        if is_maximizing:
            max_eval = -math.inf
            for from_pos, to_pos in all_moves:
                board.make_move(from_pos, to_pos)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for from_pos, to_pos in all_moves:
                board.make_move(from_pos, to_pos)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval