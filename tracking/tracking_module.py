import mediapipe as mp
import cv2

class TrackingModule:
    """
    MediaPipe Hands interface.
    Processes frames and returns normalized 21-point hand landmark data.

    MediaPipe landmark indices used in gesture classification:
        4  - Thumb tip
        8  - Index finger tip
        12 - Middle finger tip
        16 - Ring finger tip
        20 - Pinky tip
        0  - Wrist
        5  - Index finger MCP (base knuckle)
    """

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

    def get_landmarks(self, frame):
        """
        Processes a BGR frame and returns a tuple of:
            (landmark_list, hand_landmarks_proto)
        or None if no hand is detected.

        - landmark_list: the 21 individual landmark objects used by GestureModule
        - hand_landmarks_proto: the original MediaPipe proto object required by draw_landmarks
        Storing both here avoids needing to reconstruct the proto later.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            return hand.landmark, hand
        return None

    def draw_landmarks(self, frame, landmark_data):
        """
        Draws MediaPipe hand skeleton overlay onto the frame.
        Accepts the full tuple returned by get_landmarks, or None.
        Returns the annotated frame unchanged if no landmarks.
        """
        if landmark_data is None:
            return frame

        _, hand_proto = landmark_data
        annotated = frame.copy()
        self.mp_draw.draw_landmarks(
            annotated,
            hand_proto,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_draw_styles.get_default_hand_landmarks_style(),
            self.mp_draw_styles.get_default_hand_connections_style()
        )
        return annotated