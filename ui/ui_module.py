import cv2
import numpy as np
import datetime

# --- Layout constants ---
PALETTE_Y          = 30        # Y center of color circles
PALETTE_CIRCLE_R   = 20        # Radius of each color circle
PALETTE_SPACING    = 60        # Space between circle centers
HOVER_FRAMES       = 20        # Frames to hover before selecting
SLIDER_X           = None      # Set dynamically based on frame width
SLIDER_TOP_PAD     = 60        # Pixels from top where slider starts
SLIDER_BOT_PAD     = 60        # Pixels from bottom where slider ends
SLIDER_WIDTH       = 40        # Width of the slider strip
BRUSH_MIN          = 2
BRUSH_MAX          = 40

# --- Color palette (BGR) ---
COLORS = [
    ("Red",    (0,   0,   255)),
    ("Blue",   (255, 0,   0  )),
    ("Green",  (0,   200, 0  )),
    ("Yellow", (0,   255, 255)),
    ("Black",  (0,   0,   0  )),
]


class UIModule:
    """
    Draws the color palette and brush size slider onto the display frame.
    Handles hover-based selection for both.
    Also handles cursor rendering in whiteboard mode and saving.
    """

    def __init__(self, width, height):
        self.width  = width
        self.height = height

        # Build palette circle positions centered at top of screen
        n = len(COLORS)
        total_w = (n - 1) * PALETTE_SPACING
        start_x = (width - total_w) // 2
        self.palette_positions = [
            (start_x + i * PALETTE_SPACING, PALETTE_Y)
            for i in range(n)
        ]

        # Slider strip on right side
        self.slider_x     = width - SLIDER_WIDTH - 10
        self.slider_top   = SLIDER_TOP_PAD
        self.slider_bot   = height - SLIDER_BOT_PAD

        # Hover state
        self._hover_color_idx   = -1
        self._hover_color_count = 0
        self._hover_slider      = False
        self._hover_slider_count = 0

        self.active_color_idx = 0   # Index into COLORS

    # ------------------------------------------------------------------ #
    #  Main update — call every frame before displaying                   #
    # ------------------------------------------------------------------ #

    def update(self, display, norm_position, gesture, canvas):
        """
        Processes fingertip position against UI zones and draws all UI elements.
        Modifies canvas brush state directly when a selection is made.
        Returns the annotated display frame.
        """
        px = int(norm_position[0] * self.width)
        py = int(norm_position[1] * self.height)

        # Only interact with UI during idle or draw (not erase)
        if gesture in ("idle", "draw"):
            self._check_palette_hover(px, py, canvas)
            self._check_slider_hover(px, py, canvas)

        display = self._draw_palette(display)
        display = self._draw_slider(display, canvas.brush_size)
        return display

    # ------------------------------------------------------------------ #
    #  Hover detection                                                     #
    # ------------------------------------------------------------------ #

    def _check_palette_hover(self, px, py, canvas):
        hit = -1
        for i, (cx, cy) in enumerate(self.palette_positions):
            if abs(px - cx) < PALETTE_CIRCLE_R and abs(py - cy) < PALETTE_CIRCLE_R:
                hit = i
                break

        if hit == self._hover_color_idx and hit != -1:
            self._hover_color_count += 1
            if self._hover_color_count >= HOVER_FRAMES:
                self.active_color_idx = hit
                canvas.set_color(COLORS[hit][1])
                self._hover_color_count = 0
        else:
            self._hover_color_idx   = hit
            self._hover_color_count = 0

    def _check_slider_hover(self, px, py, canvas):
        in_slider = (
            self.slider_x <= px <= self.slider_x + SLIDER_WIDTH and
            self.slider_top <= py <= self.slider_bot
        )

        if in_slider:
            self._hover_slider_count += 1
            if self._hover_slider_count >= 3:  # Respond quickly for slider
                ratio = 1.0 - (py - self.slider_top) / (self.slider_bot - self.slider_top)
                size  = int(BRUSH_MIN + ratio * (BRUSH_MAX - BRUSH_MIN))
                canvas.set_brush_size(size)
        else:
            self._hover_slider_count = 0

    # ------------------------------------------------------------------ #
    #  Drawing UI elements                                                 #
    # ------------------------------------------------------------------ #

    def _draw_palette(self, display):
        for i, ((cx, cy), (name, bgr)) in enumerate(zip(self.palette_positions, COLORS)):
            # Fill circle
            cv2.circle(display, (cx, cy), PALETTE_CIRCLE_R, bgr, -1)
            # White border always, thicker ring for active color
            thickness = 3 if i == self.active_color_idx else 1
            cv2.circle(display, (cx, cy), PALETTE_CIRCLE_R, (255, 255, 255), thickness)

            # Hover progress arc
            if self._hover_color_idx == i and self._hover_color_count > 0:
                progress = self._hover_color_count / HOVER_FRAMES
                angle    = int(360 * progress)
                cv2.ellipse(display, (cx, cy), (PALETTE_CIRCLE_R + 5, PALETTE_CIRCLE_R + 5),
                            -90, 0, angle, (255, 255, 255), 2)
        return display

    def _draw_slider(self, display, current_size):
        # Background strip
        cv2.rectangle(display,
                       (self.slider_x, self.slider_top),
                       (self.slider_x + SLIDER_WIDTH, self.slider_bot),
                       (60, 60, 60), -1)
        cv2.rectangle(display,
                       (self.slider_x, self.slider_top),
                       (self.slider_x + SLIDER_WIDTH, self.slider_bot),
                       (180, 180, 180), 1)

        # Filled portion showing current size
        ratio    = (current_size - BRUSH_MIN) / (BRUSH_MAX - BRUSH_MIN)
        fill_y   = int(self.slider_bot - ratio * (self.slider_bot - self.slider_top))
        cv2.rectangle(display,
                       (self.slider_x, fill_y),
                       (self.slider_x + SLIDER_WIDTH, self.slider_bot),
                       (200, 200, 200), -1)

        # Label
        cv2.putText(display, "SIZE", (self.slider_x, self.slider_top - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(display, str(current_size),
                    (self.slider_x + 8, self.slider_bot + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        return display

    # ------------------------------------------------------------------ #
    #  Cursor (whiteboard mode only)                                       #
    # ------------------------------------------------------------------ #

    def draw_cursor(self, display, norm_position, gesture, brush_size):
        """
        Draws a small cursor at the index fingertip position.
        Color and size reflect current gesture state.
        """
        px = int(norm_position[0] * self.width)
        py = int(norm_position[1] * self.height)

        if gesture == "draw":
            # Filled dot in active brush color
            bgr = COLORS[self.active_color_idx][1]
            cv2.circle(display, (px, py), max(4, brush_size // 2), bgr, -1)
            cv2.circle(display, (px, py), max(4, brush_size // 2), (255, 255, 255), 1)
        elif gesture == "erase":
            # Semi-transparent circle showing erase radius
            overlay = display.copy()
            cv2.circle(overlay, (px, py), brush_size, (180, 180, 180), -1)
            cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)
            cv2.circle(display, (px, py), brush_size, (180, 180, 180), 1)
        else:
            # Idle — small white ring
            cv2.circle(display, (px, py), 6, (255, 255, 255), 1)
        return display

    # ------------------------------------------------------------------ #
    #  Save                                                                #
    # ------------------------------------------------------------------ #

    def save(self, canvas, canvas_only_mode, webcam_frame=None):
        """
        Saves the current drawing as a timestamped PNG.
        In whiteboard mode saves clean white background version.
        In camera mode saves the composited webcam+drawing version.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"airdraw_{timestamp}.png"

        if canvas_only_mode:
            image = canvas.overlay_on_white()
        else:
            image = canvas.overlay(webcam_frame) if webcam_frame is not None else canvas.overlay_on_white()

        cv2.imwrite(filename, image)
        print(f"Saved: {filename}")
        return filename
    
    # ------------------------------------------------------------------ #
    #  UI Zone Guard                                                       #
    # ------------------------------------------------------------------ #
    
    def is_over_ui(self, norm_position):
        """
        Returns True if the fingertip is currently over any UI zone.
        Used by main.py to suppress drawing while interacting with UI.
        """
        px = int(norm_position[0] * self.width)
        py = int(norm_position[1] * self.height)

        # Check palette zone — full top strip
        if py < PALETTE_Y + PALETTE_CIRCLE_R + 10:
            return True

        # Check slider zone
        if (self.slider_x - 10 <= px <= self.slider_x + SLIDER_WIDTH + 10 and
                self.slider_top <= py <= self.slider_bot):
            return True

        return False
    
    