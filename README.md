# AirDraw

Gesture-based air drawing application using MediaPipe Hands and OpenCV.

## Getting Started

1. Create a virtual environment:
   ```
   python -m venv venv
   ```
   > **Note:** If you are on Python 3.13+, make sure to create the venv
   > using Python 3.11 specifically: `py -3.11 -m venv venv`

2. Activate it:
   - Windows:   `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > OS is detected automatically — no manual configuration needed.
   > Mac installs mediapipe==0.10.9, Windows installs mediapipe==0.10.13.
   
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
| Hover fingertip over color circle (top) | Select color |
| Hover fingertip over right side slider | Adjust brush size |
| Press `v` | Toggle whiteboard mode (hides webcam feed) |
| Press `c` | Clear canvas |
| Press `s` | Save drawing as PNG |
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
