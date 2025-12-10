import numpy as np
import cv2
from typing import Tuple

class Projector:
    def __init__(self, H_path: str = "H.npy", use_homography: bool = True):
        self.H = None
        self.use = use_homography
        if use_homography:
            try:
                self.H = np.load(H_path)
            except Exception:
                self.H = None
                print(f"[WARN] Could not load homography from {H_path}; homography disabled.")

    def to_world(self, x_px: int, y_px: int) -> Tuple[float, float]:
        if self.use and self.H is not None:
            pt = np.array([[x_px, y_px]], dtype=np.float32).reshape(1,1,2)
            proj = cv2.perspectiveTransform(pt, self.H).reshape(2)
            return float(proj[0]), float(proj[1])
        else:
            return float(x_px), float(y_px)
