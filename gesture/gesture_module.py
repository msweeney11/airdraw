import math

# --- Landmark index constants (MediaPipe Hands) ---
WRIST        = 0
THUMB_TIP    = 4
THUMB_IP     = 3
INDEX_TIP    = 8
INDEX_PIP    = 6
INDEX_MCP    = 5
MIDDLE_TIP   = 12
MIDDLE_PIP   = 10
MIDDLE_MCP   = 9
RING_TIP     = 16
RING_PIP     = 14
RING_MCP     = 13
PINKY_TIP    = 20
PINKY_PIP    = 18
PINKY_MCP    = 17

# --- Threshold tuning ---
FINGER_CURL_RATIO  = 0.8
IDLE_FRAMES        = 3

def _distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def _is_finger_extended(tip, pip, mcp, wrist):
    tip_above_pip = tip.y < pip.y
    tip_extended = _distance(tip, wrist) > _distance(mcp, wrist) * FINGER_CURL_RATIO
    return tip_above_pip and tip_extended

class GestureModule:
    """
    Translates raw MediaPipe landmarks into one of three core gestures:

        draw   - Index finger extended, other fingers curled into fist
                 Position follows the index fingertip.

        erase  - Open palm: index, middle, ring, and pinky all extended.
                 Position follows the center of the palm (index MCP).

        idle   - Any other hand shape; no drawing action.
    """


    def __init__(self):
        self._prev_gesture = "idle"
        self._idle_counter = 0

    def interpret(self, landmarks):
        """
        Given a list of 21 MediaPipe landmark objects, returns:
            (gesture_name: str, position: (float, float))

        position is normalized (x, y) in [0, 1], suitable for
        scaling to canvas pixel coordinates in DrawingModule.
        """
        lm = list(landmarks)

        index_extended  = _is_finger_extended(lm[INDEX_TIP],  lm[INDEX_PIP],  lm[INDEX_MCP],  lm[WRIST])
        middle_extended = _is_finger_extended(lm[MIDDLE_TIP], lm[MIDDLE_PIP], lm[MIDDLE_MCP], lm[WRIST])
        ring_extended   = _is_finger_extended(lm[RING_TIP],   lm[RING_PIP],   lm[RING_MCP],   lm[WRIST])
        pinky_extended  = _is_finger_extended(lm[PINKY_TIP],  lm[PINKY_PIP],  lm[PINKY_MCP],  lm[WRIST])

        
        # --- Gesture classification (priority order matters) ---

        # ERASE: open palm — all four fingers extended
        if index_extended and middle_extended and ring_extended and pinky_extended:
            gesture = "erase"
            self._idle_counter = 0
            position = (lm[INDEX_MCP].x, lm[INDEX_MCP].y)
        
        # DRAW: index extended + other fingers curled into fist
        elif index_extended and not middle_extended and not ring_extended and not pinky_extended:
            gesture = "draw"
            self._idle_counter = 0
            position = (lm[INDEX_TIP].x, lm[INDEX_TIP].y)

        # IDLE: everything else (fist, partial fingers, transitional shapes)
        else:
            self._idle_counter += 1
            position = (lm[INDEX_TIP].x, lm[INDEX_TIP].y)
            gesture = "idle"

        self._prev_gesture = gesture
        return gesture, position

    def reset(self):
        self._prev_gesture = "idle"
        self._idle_counter = 0