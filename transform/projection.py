import numpy as np
import cv2
from typing import Tuple

class Projector:
    def __init__(self, settings):
        self.H = None
        if settings.use_homography:
            try:
                self.H = np.load(settings.homography_path)
            except Exception:
                self.H = None
                print(f"[WARN] Could not load homography from {settings.homography_path}; homography disabled.")

    def to_world(self, x_px: int, y_px: int) -> Tuple[float, float]:
        if not len(self.H):
            # Return screen coordinates as fallback
            return float(x_px), float(y_px)
        else:
            pt = np.array([[x_px, y_px]], dtype=np.float32).reshape(1,1,2)
            proj = cv2.perspectiveTransform(pt, self.H).reshape(2)
            return float(proj[0]), float(proj[1])
