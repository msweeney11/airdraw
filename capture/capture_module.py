import cv2

class CaptureModule:
    """
    OpenCV wrapper for webcam capture.
    Handles frame acquisition and basic preprocessing (flip for mirror effect).
    """

    def __init__(self, camera_index=0, width=640, height=480):
        ## self.cap = cv2.VideoCapture(camera_index) USE THIS IF YOU ARE ON WINDOWS, COMMENT OUT LINE BELOW THIS
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open webcam at index {camera_index}.")

    def read_frame(self):
        """
        Reads a single frame from the webcam.
        Returns a horizontally flipped BGR frame, or None on failure.
        Flipping creates a natural mirror effect for the user.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)

    def release(self):
        self.cap.release()


