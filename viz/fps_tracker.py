# utils/fps_tracker.py
import time

class FPSTracker:
    def __init__(self):
        self.last_ts = None
        self.fps_history = []

    def update(self):
        """Call once per frame. Returns current FPS."""
        now = time.time()
        if self.last_ts is None:
            self.last_ts = now
            return 0.0  # first frame

        dt = now - self.last_ts
        self.last_ts = now

        if dt > 0:
            fps = 1.0 / dt
            self.fps_history.append(fps)
            return fps
        return 0.0

    @property
    def current(self):
        return self.fps_history[-1] if self.fps_history else 0.0

    @property
    def average(self):
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)

    @property
    def minimum(self):
        return min(self.fps_history) if self.fps_history else 0.0

    @property
    def maximum(self):
        return max(self.fps_history) if self.fps_history else 0.0
