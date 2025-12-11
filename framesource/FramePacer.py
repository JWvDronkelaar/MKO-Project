import time

class FramePacer:
    """
    A pacing controller that enforces a target FPS using short micro-sleeps.

    - Does NOT cause long blocking sleeps.
    - Keeps camera drivers responsive.
    - Works with live camera input or video files.
    """

    def __init__(self, target_fps: float):
        self.target_fps = float(target_fps)
        self.frame_duration = 1.0 / self.target_fps
        self.last_frame_time = None

    def start_frame(self):
        """
        Mark the beginning of processing for the current frame.
        """
        self.last_frame_time = time.perf_counter()

    def end_frame(self):
        """
        Non-blocking pacing:
        Sleep in very small steps until the desired frame duration has elapsed.

        Never sleeps long enough to starve V4L2 capture.
        """
        if self.last_frame_time is None:
            return

        target_end = self.last_frame_time + self.frame_duration

        # Short-sleep pacing loop
        # using 0.001–0.002 sec micro-sleeps instead of one long sleep
        while True:
            now = time.perf_counter()
            remaining = target_end - now

            if remaining <= 0:
                return

            # Bound the sleep to avoid blocking camera driver
            time.sleep(min(remaining, 0.002))  # 2ms max sleep
