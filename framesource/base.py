# base.py
import threading
import time
from abc import ABC, abstractmethod


class FrameSource(ABC):
    """
    Threaded frame source.
    Provides frames and a running frame counter.
    """

    def __init__(self):
        self.frame_number = 0
        self._running = False
        self._thread = None

        self._latest_frame = None
        self._latest_frame_number = None

    @property
    def is_alive(self):
        return self._running and self._latest_frame is not None

    #
    # Public API
    #
    def start(self):
        print("Start the capture thread.")
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        print("Stop the capture thread.")
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        self.release()

    def read(self):
        """
        Non-blocking: returns the most recent (frame, frame_number).
        Returns (None, None) if no frame has arrived yet.
        """
        return self._latest_frame, self._latest_frame_number

    #
    # Internal loop
    #
    def _capture_loop(self):
        while self._running:
            frame = self._read_frame_blocking()
            if frame is None:
                # File ended or camera error
                self._running = False
                break

            self.frame_number += 1
            self._latest_frame = frame
            self._latest_frame_number = self.frame_number

    #
    # Methods subclasses must implement
    #
    @abstractmethod
    def _read_frame_blocking(self):
        """Return a raw frame or None."""
        ...

    @abstractmethod
    def release(self):
        """Release hardware or file handles."""
        ...
