import time

class FramePacer:
    """
    Non-blocking frame pacer as a context manager.
    Usage:
        pacer = FramePacer(target_fps=30)
        while running:
            frame, frame_number = source.read()
            if frame is None:
                continue

            with pacer as should_process:
                if not should_process:
                    continue  # skip this frame

                # --- detection / tracking / processing ---
    """
    def __init__(self, target_fps: float):
        self.target_interval = 1.0 / target_fps
        self._last_process_time = time.perf_counter()
        self.should_process = True

    def __enter__(self):
        now = time.perf_counter()
        elapsed = now - self._last_process_time
        if elapsed >= self.target_interval:
            self.should_process = True
            self._last_process_time = now
        else:
            self.should_process = False
        return self.should_process

    def __exit__(self, exc_type, exc_val, exc_tb):
        # nothing to do on exit
        pass
