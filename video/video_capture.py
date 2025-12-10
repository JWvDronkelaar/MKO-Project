import cv2

class VideoSource:
    def __init__(self, settings):
        self.source = settings.camera_index
        self.cap = cv2.VideoCapture(self.source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
        self.frame_number = 0

    def __iter__(self):
        return self

    def __next__(self):
        ok, frame = self.cap.read()
        if not ok:
            self.cap.release()
            raise StopIteration
        self.frame_number += 1
        return frame, self.frame_number

    def release(self):
        if self.cap:
            self.cap.release()
