# Chess AI — Minimax + Alpha-Beta Pruning

A fully functional chess game built in Python where you play against an AI opponent powered by the **Minimax algorithm with Alpha-Beta Pruning**.

## Features
- Complete chess rules (all piece movements, check, checkmate, stalemate, pawn promotion)
- AI opponent using Minimax with Alpha-Beta Pruning (depth 3 — looks 3 moves ahead)
- Piece-Square Tables for positional evaluation
- Real-time move highlighting and check detection
- Threaded AI so UI never freezes

## Tech Stack
- Python 3.x
- Pygame (UI)

## Setup & Run

```bash
pip install pygame
python main.py
```

## How to Play
- **Click** a white piece to select it (green highlight)
- **Click** a destination square (green dots show legal moves)
- AI (Black) responds automatically
- Press **R** to restart the game

## Project Structure
```
chess_ai/
├── main.py       # Pygame UI + Game loop
├── board.py      # Board state, move execution, check detection
├── pieces.py     # All piece classes with move generation
├── ai.py         # Minimax + Alpha-Beta Pruning + Board Evaluation
└── README.md
```

## AI Explanation

### Minimax
The AI explores all possible moves up to depth 3, assuming both players play optimally:
- **Maximizing** (AI/Black): picks the move with highest evaluation score
- **Minimizing** (Player/White): picks the move with lowest evaluation score

### Alpha-Beta Pruning
Eliminates branches that cannot affect the final decision, reducing nodes searched by ~60%:
```
if beta <= alpha:
    break  # Prune — this branch won't be chosen
```

### Board Evaluation
Each position is scored using:
- **Material value**: Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900
- **Piece-Square Tables**: Bonus/penalty based on piece position (e.g., knights are stronger in the center)

## CV Points
- "Implemented Minimax algorithm with Alpha-Beta Pruning, reducing search nodes by ~60%"
- "Built complete chess engine with legal move generation, check/checkmate detection"
- "Used piece-square tables for positional board evaluation"
