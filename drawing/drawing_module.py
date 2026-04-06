import cv2
import numpy as np

# --- Default brush/tool state ---
DEFAULT_COLOR      = (0, 0, 255)   # Red in BGR
DEFAULT_BRUSH_SIZE = 5
CANVAS_ALPHA       = 0.6           # Blend weight of canvas over webcam feed


class DrawingModule:
    """
    Maintains a persistent drawing canvas and handles gesture-driven rendering.

    Brush state is separated from stroke logic to make future tool expansion
    (color picker, size slider) straightforward — just update self.brush_color
    or self.brush_size from wherever tool selection is handled.

    Supported gestures (passed in from GestureModule):
        draw  - Draws a line segment from the last draw position to current.
        erase - Erases a circular area around the current position.
        idle  - Lifts the "pen"; breaks stroke continuity.
    """

    def __init__(self, width=640, height=480):
        self.width  = width
        self.height = height

        # Transparent canvas: BGRA so we can composite cleanly
        self.canvas = np.zeros((height, width, 4), dtype=np.uint8)

        # --- Brush / tool state ---
        self.brush_color = DEFAULT_COLOR   
        self.brush_size  = DEFAULT_BRUSH_SIZE
        self.active_tool = "brush"         # "brush" | "eraser" (future: "fill", etc.)

        self._prev_position = None         # Last draw position in pixel coords
        self._is_drawing    = False        # True while draw gesture is active

    # ------------------------------------------------------------------ #
    #  Core gesture handler                                                #
    # ------------------------------------------------------------------ #

    def handle_gesture(self, gesture: str, norm_position: tuple):
        """
        Called every frame with the current gesture and normalized (x, y).
        Converts normalized coords to pixel coords and dispatches to the
        appropriate drawing action.
        """
        px, py = self._to_pixels(norm_position)

        if gesture == "draw":
            self._handle_draw(px, py)
        elif gesture == "erase":
            self._handle_erase(px, py)
        elif gesture == "idle":
            self._handle_idle()

    # ------------------------------------------------------------------ #
    #  Drawing actions                                                     #
    # ------------------------------------------------------------------ #

    def _handle_draw(self, x: int, y: int):
        """
        Draws a smooth line segment from the previous draw position to (x, y).
        On the first draw frame after idle, just records the start point.
        """
        if self._is_drawing and self._prev_position is not None:
            x0, y0 = self._prev_position
            # BGRA: append full alpha (255) to the brush color
            color_bgra = (*self.brush_color, 255)
            cv2.line(self.canvas, (x0, y0), (x, y), color_bgra, self.brush_size,
                     lineType=cv2.LINE_AA)
        self._is_drawing    = True
        self._prev_position = (x, y)

    def _handle_erase(self, x: int, y: int):
        """
        Erases a circular region by zeroing out the canvas alpha channel.
        This is non-destructive relative to the webcam feed.
        """
        cv2.circle(self.canvas, (x, y), self.brush_size * 3, (0, 0, 0, 0), -1)
        self._prev_position = None
        self._is_drawing    = False

    def _handle_idle(self):
        """Lifts the pen, next draw gesture will start a new stroke."""
        self._prev_position = None
        self._is_drawing    = False

    # ------------------------------------------------------------------ #
    #  Rendering                                                           #
    # ------------------------------------------------------------------ #
    def overlay_on_white(self):
            """Returns the drawing on a plain white background, no webcam feed."""
            white = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
            bgr   = self.canvas[:, :, :3]
            alpha = self.canvas[:, :, 3:4].astype(np.float32) / 255.0
            white_f  = white.astype(np.float32)
            canvas_f = bgr.astype(np.float32)
            blended  = white_f * (1 - alpha) + canvas_f * alpha
            return blended.astype(np.uint8)
    
    def overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Composites the drawing canvas over the webcam frame.
        Uses the canvas alpha channel so only drawn pixels are visible.
        Returns a BGR frame ready for display.
        """
        bgr   = self.canvas[:, :, :3]
        alpha = self.canvas[:, :, 3:4].astype(np.float32) / 255.0

        frame_f   = frame.astype(np.float32)
        canvas_f  = bgr.astype(np.float32)
        blended   = frame_f * (1 - alpha) + canvas_f * alpha
        return blended.astype(np.uint8)

    def clear(self):
        """Clears the entire canvas."""
        self.canvas[:] = 0

    # ------------------------------------------------------------------ #
    #  Brush / tool state helpers (for future UI integration)             #
    # ------------------------------------------------------------------ #

    def set_color(self, bgr_color: tuple):
        """Update active brush color. Accepts a BGR tuple, e.g. (0, 255, 0)."""
        self.brush_color = bgr_color

    def set_brush_size(self, size: int):
        """Update active brush size in pixels."""
        self.brush_size = max(1, size)

    # ------------------------------------------------------------------ #
    #  Utilities                                                           #
    # ------------------------------------------------------------------ #

    def _to_pixels(self, norm_pos: tuple) -> tuple:
        """Converts normalized (x, y) in [0,1] to canvas pixel coordinates."""
        x = int(norm_pos[0] * self.width)
        y = int(norm_pos[1] * self.height)
        # Clamp to canvas bounds
        x = max(0, min(self.width  - 1, x))
        y = max(0, min(self.height - 1, y))
        return x, y

    def overlay_on_white(self):
        """Returns the drawing on a plain white background, no webcam feed."""
        white    = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        bgr      = self.canvas[:, :, :3]
        alpha    = self.canvas[:, :, 3:4].astype(np.float32) / 255.0
        white_f  = white.astype(np.float32)
        canvas_f = bgr.astype(np.float32)
        blended  = white_f * (1 - alpha) + canvas_f * alpha
        return blended.astype(np.uint8)

