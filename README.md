# AirDraw

Gesture-based air drawing application using MediaPipe Hands and OpenCV.

## Getting Started

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate it:
   - Windows:   `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run:
   ```
   python main.py
   ```

## Controls

| Gesture | Action |
|---|---|
| Index finger extended + other fingers curled into fist | Draw |
| Open palm (all 4 fingers extended) | Erase |
| Any other shape / fist | Idle (lift pen) |
| Press `c` | Clear canvas |
| Press `q` | Quit |

## Project Structure

```
airdraw/
├── main.py                      # Entry point — runs the main loop
├── capture/
│   └── capture_module.py        # OpenCV webcam wrapper
├── tracking/
│   └── tracking_module.py       # MediaPipe Hands interface
├── gesture/
│   └── gesture_module.py        # Landmark-distance gesture classification
├── drawing/
│   └── drawing_module.py        # Canvas, brush state, stroke rendering
├── ui/                          # UI overlays and menus
├── requirements.txt
└── README.md
```
