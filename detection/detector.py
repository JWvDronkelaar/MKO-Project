from ultralytics import YOLO
import numpy as np
import supervision as sv
from typing import Optional

class PeopleDetector:
    def __init__(self, model_path: str, conf: float = 0.1, iou: float = 0.5, device: Optional[str] = None):
        self.conf = conf
        self.iou = iou
        self.model = YOLO(model_path, task="detect")
        # # try to move to GPU if available and requested
        # if device is None:
        #     try:
        #         import torch
        #         device = "cuda" if torch.cuda.is_available() else "cpu"
        #     except Exception:
        #         device = "cpu"
        # try:
        #     self.model.to(device)
        # except Exception:
        #     # not fatal; model will use default device
        #     pass

    def detect(self, frame):
        """Return supervision Detections for the frame (filtered by person class later)."""
        res = self.model.predict(source=frame, verbose=False, conf=self.conf, iou=self.iou, device="cuda")[0]
        det = sv.Detections.from_ultralytics(res)
        return det, res  # return both for name mapping if needed
