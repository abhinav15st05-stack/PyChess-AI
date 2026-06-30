"""
board.py - Chess board logic: setup, execution, undo, and state detection.
"""

from pieces import Pawn, Rook, Knight, Bishop, Queen, King
import copy


class Board:
    def __init__(self):
        self.grid = [[None] * 8 for _ in range(8)]
        self.current_turn = 'white'
        self.move_history = []   
        self.setup_board()

    # ─── Board Setup ──────────────────────────────────────────────────────────

    def setup_board(self):
        """Standard chess starting position."""
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, PieceClass in enumerate(order):
            self.grid[0][col] = PieceClass('black')
            self.grid[7][col] = PieceClass('white')

        for col in range(8):
            self.grid[1][col] = Pawn('black')
            self.grid[6][col] = Pawn('white')

    # ─── Move Execution ───────────────────────────────────────────────────────

    def make_move(self, from_pos, to_pos):
        """Executes a move and updates board state. Returns captured piece if any."""
        fr, fc = from_pos
        tr, tc = to_pos

        piece = self.grid[fr][fc]
        captured = self.grid[tr][tc]

        # Save history for undo functionality
        self.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'piece': piece,
            'captured': captured,
            'had_moved': piece.has_moved
        })

        self.grid[tr][tc] = piece
        self.grid[fr][fc] = None
        piece.has_moved = True

        # Default pawn promotion to Queen
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and tr == 0) or (piece.color == 'black' and tr == 7):
                self.grid[tr][tc] = Queen(piece.color)

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        return captured

    def undo_move(self):
        """Reverts the last move (required for AI search tree)."""
        if not self.move_history:
            return

        last = self.move_history.pop()
        fr, fc = last['from']
        tr, tc = last['to']

        self.grid[fr][fc] = last['piece']
        self.grid[tr][tc] = last['captured']
        last['piece'].has_moved = last['had_moved']

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    # ─── Move Validation ──────────────────────────────────────────────────────

    def get_raw_moves(self, row, col):
        """Gets all pseudo-legal moves for a piece."""
        piece = self.grid[row][col]
        if piece is None:
            return []
        return piece.valid_moves(row, col, self.grid)

    def get_legal_moves(self, row, col):
        """Filters moves to ensure king safety."""
        piece = self.grid[row][col]
        if piece is None or piece.color != self.current_turn:
            return []

        legal = []
        for move in self.get_raw_moves(row, col):
            self.make_move((row, col), move)
            self.current_turn = piece.color   # Temporarily reset for check detection
            in_check = self.is_in_check(piece.color)
            self.current_turn = 'black' if piece.color == 'white' else 'white'
            self.undo_move()
            
            if not in_check:
                legal.append(move)

        return legal

    def get_all_legal_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    saved_turn = self.current_turn
                    self.current_turn = color
                    for move in self.get_legal_moves(row, col):
                        moves.append(((row, col), move))
                    self.current_turn = saved_turn
        return moves

    # ─── Game State Detection ─────────────────────────────────────────────────

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_in_check(self, color):
        """Checks if the given color's king is currently under attack."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        opponent = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == opponent:
                    if king_pos in piece.valid_moves(row, col, self.grid):
                        return True
        return False

    def is_checkmate(self, color):
        saved = self.current_turn
        self.current_turn = color
        all_moves = self.get_all_legal_moves(color)
        self.current_turn = saved
        return len(all_moves) == 0 and self.is_in_check(color)

    def is_stalemate(self, color):
        saved = self.current_turn
        self.current_turn = color
        all_moves = self.get_all_legal_moves(color)
        self.current_turn = saved
        return len(all_moves) == 0 and not self.is_in_check(color)