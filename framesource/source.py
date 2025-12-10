import cv2
from .base import FrameSource

class VideoFileSource(FrameSource):
    def __init__(self, settings):
        super().__init__()
        self.source = settings.camera_index
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)


    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None, None
        self.frame_number += 1
        return frame, self.frame_number


    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None


class CameraSource(FrameSource):
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

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None, None
        self.frame_number += 1
        return frame, self.frame_number

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
