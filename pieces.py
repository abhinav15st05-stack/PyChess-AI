"""
pieces.py - Chess piece classes and their move generation logic.
"""

class Piece:
    def __init__(self, color):
        self.color = color          
        self.has_moved = False      # Tracks if piece has moved (useful for pawns/castling)

    def valid_moves(self, row, col, board):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.color[0].upper()}{self.__class__.__name__[0]}"


class Pawn(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        direction = -1 if self.color == 'white' else 1  
        start_row = 6 if self.color == 'white' else 1

        # Move forward by one square
        nr = row + direction
        if 0 <= nr < 8 and board[nr][col] is None:
            moves.append((nr, col))
            # Move forward by two squares on first move
            if row == start_row and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        # Diagonal captures
        for dc in [-1, 1]:
            nc = col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target is not None and target.color != self.color:
                    moves.append((nr, nc))

        return moves


class Rook(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class Knight(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None or board[r][c].color != self.color:
                    moves.append((r, c))
        return moves


class Bishop(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class Queen(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        # Queen moves combine Rook and Bishop logic
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves


class King(Piece):
    def valid_moves(self, row, col, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        moves.append((r, c))
        return moves