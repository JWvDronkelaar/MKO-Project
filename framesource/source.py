# video_file_source.py
import cv2
from .base import FrameSource


class VideoFileSource(FrameSource):
    """
    Threaded reader for video files.
    """

    def __init__(self, settings):
        super().__init__()
        self.path = settings.video
        self.cap = cv2.VideoCapture(self.path)

    def _read_frame_blocking(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None


class CameraSource(FrameSource):
    """
    Threaded reader for live cameras.
    """

    def __init__(self, settings):
        super().__init__()
        self.camera_index = settings.camera_index

        self.cap = cv2.VideoCapture(self.camera_index)
        if settings.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
        if settings.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        if hasattr(settings, "fps") and settings.fps:
            self.cap.set(cv2.CAP_PROP_FPS, settings.fps)

    def _read_frame_blocking(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
