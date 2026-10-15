# Flippy (Web Edition)

A Reversi / Othello board game built with Python and Pygame-CE. Play against an AI opponent on an 8x8 grid.

Playable locally and in modern web browsers via WebAssembly ([Pygbag](https://pygame-web.github.io/)).

## How to Run Locally

### Prerequisites
- Python 3.10+
- `pip install pygame-ce pygbag`

### Play Locally
```bash
python main.py
```

### Run in Browser Locally
```bash
python -m pygbag main.py
```
Open `http://localhost:8000` in your web browser.

## Controls
- **Mouse Click**: Select space to place tile
- **New Game**: Restart match
- **Hints**: Toggle legal move hints
