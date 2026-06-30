# Chess AI — Minimax + Alpha-Beta Pruning

A fully functional chess game built in Python where you play against an AI opponent powered by the **Minimax algorithm with Alpha-Beta Pruning**.

## Features
- Complete chess rules (all piece movements, check, checkmate, stalemate, castling, and pawn underpromotion)
- AI opponent using Minimax with Alpha-Beta Pruning (depth 3 — looks 3 moves ahead)
- Move Ordering & Tie-Breaking applied to make the AI faster and more unpredictable
- Piece-Square Tables for positional evaluation
- Modern minimalist UI with real-time move highlighting, check detection, and timer clocks
- Threaded AI with deep-copied states so the UI never freezes

## Tech Stack
- Python 3.x
- Pygame (UI)

## Setup & Run

```bash
pip install -r requirements.txt
python main.py
```


## How to Play
- **Click** a white piece to select it (highlighted with a premium gold glow)
- **Click** a destination square (transparent dots show legal moves)
- AI (Black) responds automatically
- **Pawn Promotion:** If your pawn reaches the end, a popup menu will let you choose your piece (Queen, Rook, Bishop, or Knight)
- Use the sidebar buttons to **Restart** or **Resign** at any time

## Project Structure
```
chess_ai/
├── main.py             # Pygame UI, game loop, timers & buttons
├── board.py            # Board state, move execution, check/castling detection
├── pieces.py           # All piece classes with move generation rules
├── ai.py               # Minimax + Alpha-Beta Pruning + Board Evaluation
├── requirements.txt    # Dependencies
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


