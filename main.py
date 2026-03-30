import cv2
from capture.capture_module import CaptureModule
from tracking.tracking_module import TrackingModule
from gesture.gesture_module import GestureModule
from drawing.drawing_module import DrawingModule
from ui.ui_module import UIModule

def main():
    capture = CaptureModule()
    tracker = TrackingModule()
    gesture_interpreter = GestureModule()

    first_frame = capture.read_frame()
    h, w = first_frame.shape[:2]
    canvas   = DrawingModule(width=w, height=h)
    ui       = UIModule(width=w, height=h)

    canvas_only_mode = False
    gesture          = "idle"
    position         = (0.5, 0.5)
    latest_frame     = first_frame

    print("AirDraw started.")
    print("  q = quit | c = clear | v = toggle whiteboard mode | s = save")

    while True:
        frame = capture.read_frame()
        if frame is None:
            print("Error: Could not read from webcam.")
            break
        latest_frame = frame

        landmark_data   = tracker.get_landmarks(frame)
        annotated_frame = tracker.draw_landmarks(frame, landmark_data)

        if landmark_data:
            landmarks, _ = landmark_data
            gesture, position = gesture_interpreter.interpret(landmarks)
            if not ui.is_over_ui(position):
                canvas.handle_gesture(gesture, position)
        else:
            gesture_interpreter.reset()
            gesture = "idle"

        # --- Build display ---
        if canvas_only_mode:
            display    = canvas.overlay_on_white()
            text_color = (0, 0, 0)
        else:
            display    = canvas.overlay(annotated_frame)
            text_color = (255, 255, 255)

        # --- UI overlay (palette + slider) ---
        display = ui.update(display, position, gesture, canvas)
        if canvas_only_mode:
            display = ui.draw_cursor(display, position, gesture, canvas.brush_size)

        # --- Gesture label ---
        gesture_label = gesture if landmark_data else "no hand"
        cv2.putText(display, f"Gesture: {gesture_label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)

        cv2.imshow("AirDraw", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas.clear()
        elif key == ord('v'):
            canvas_only_mode = not canvas_only_mode
        elif key == ord('s'):
            ui.save(canvas, canvas_only_mode, webcam_frame=latest_frame)

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()