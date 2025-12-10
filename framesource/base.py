# framesource/base.py
from abc import ABC, abstractmethod

class FrameSource(ABC):
    """
    Abstract frame source.
    Provides frames (numpy arrays) and a running frame counter.
    """

    def __init__(self):
        self.frame_number = 0

    @abstractmethod
    def read(self):
        """Return (frame, frame_number) or (None, None) if failed."""
        ...


    @abstractmethod
    def release(self):
        """Release any hardware or file handles."""
        ...
