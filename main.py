import cv2
from capture.capture_module import CaptureModule
from tracking.tracking_module import TrackingModule
from gesture.gesture_module import GestureModule
from drawing.drawing_module import DrawingModule

def main():
    capture = CaptureModule()
    tracker = TrackingModule()
    gesture_interpreter = GestureModule()
    canvas = DrawingModule(width=640, height=480)

    print("AirDraw started. Press 'q' to quit, 'c' to clear canvas.")

    while True:
        frame = capture.read_frame()
        if frame is None:
            print("Error: Could not read from webcam.")
            break

        landmark_data = tracker.get_landmarks(frame)
        annotated_frame = tracker.draw_landmarks(frame, landmark_data)

        if landmark_data:
            landmarks, _ = landmark_data
            gesture, position = gesture_interpreter.interpret(landmarks)
            canvas.handle_gesture(gesture, position)
        else:
            gesture_interpreter.reset()

        # Overlay canvas on the annotated webcam feed
        display = canvas.overlay(annotated_frame)

        # Show gesture label
        gesture_label = gesture if landmark_data else "no hand"
        cv2.putText(display, f"Gesture: {gesture_label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("AirDraw", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas.clear()

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


