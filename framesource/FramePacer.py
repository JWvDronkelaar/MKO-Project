import time
import asyncio

class AsyncFramePacer:
    """
    An asyncio-based pacing controller to maintain a target FPS.
    """
    def __init__(self, target_fps: float):
        self.target_fps = float(target_fps)
        self.frame_duration = 1.0 / self.target_fps
        self.last_frame_time = None

    def start(self):
        """Call once before entering the loop."""
        self.last_frame_time = time.perf_counter()

    async def pace(self):
        """
        Call once at the end of each processing cycle.
        Returns: actual_fps (float)
        """
        now = time.perf_counter()
        elapsed = now - self.last_frame_time

        # Sleep only if processing was faster than target frame duration
        if elapsed < self.frame_duration:
            await asyncio.sleep(self.frame_duration - elapsed)
            now = time.perf_counter()
            elapsed = now - self.last_frame_time

        self.last_frame_time = now
        return 1.0 / elapsed if elapsed > 0 else self.target_fps
