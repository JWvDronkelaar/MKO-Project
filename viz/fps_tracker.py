import time
from collections import deque
from dataclasses import dataclass

@dataclass
class FPSInfo:
    current: float
    avg: float
    max: float
    min: float

class FPSTracker:
    """
    Tracks FPS over a rolling window of frames.
    """
    def __init__(self, window_size=100):
        self.times = deque(maxlen=window_size)  # store last N timestamps
        self.last_time = None
        self.current = 0.0
        self.avg = 0.0
        self.max = 0.0
        self.min = float('inf')

    def update(self):
        now = time.perf_counter()
        if self.last_time is not None:
            dt = now - self.last_time
            if dt > 0:
                fps = 1.0 / dt
                self.current = fps
                self.times.append(fps)
                self.avg = sum(self.times) / len(self.times)
                self.max = max(self.times)
                self.min = min(self.times)
        self.last_time = now

    def reset(self):
        self.times.clear()
        self.last_time = None
        self.current = 0.0
        self.avg = 0.0
        self.max = 0.0
        self.min = float('inf')

    def get_fps(self) -> FPSInfo:
        return FPSInfo(
            current=self.current,
            avg=self.avg,
            max=self.max,
            min=self.min
        )
