from ultralytics import YOLO
import numpy as np
import supervision as sv
from typing import Optional

class PeopleDetector:
    def __init__(self, settings):
        self.conf = settings.conf_threshold
        self.iou = settings.iou_threshold
        self.model = YOLO(settings.model_path, task="detect")

        # TODO: flesh out what is exactly required? Pytorch lib had trouble installing because of pip temp path fucking up
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
        # TODO: is forcing the device here neccesary and/or even desireable? This might is either ignored or will lead
        # to a problem on non CUDA systems
        res = self.model.predict(source=frame, verbose=False, conf=self.conf, iou=self.iou, device="cuda")[0]
        det = sv.Detections.from_ultralytics(res)
        return det, res  # return both for name mapping if needed
