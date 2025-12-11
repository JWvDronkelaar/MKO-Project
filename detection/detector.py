import numpy as np
from typing import Optional

from ultralytics import YOLO
import supervision as sv
import torch

class PeopleDetector:
    def __init__(self, settings):
        self.conf = settings.conf_threshold
        self.iou = settings.iou_threshold
        self.model = YOLO(settings.model_path)
        use_gpu = settings.use_gpu

        # TODO: flesh out what is exactly required? Pytorch lib had trouble installing because of pip temp path fucking up
        # # try to move to GPU if available and requested
        if use_gpu:
            if torch.cuda.is_available():
                device = "cuda"
            else:
                print("[WARN] Detector defaulting to CPU while GPU was requested!")
                device = "cpu"
        try:
            self.model.to(device)
        except Exception:
            print(f"[WARN] Detector failed to set model to {device}")

        print(f"PeopleDetector using device '{device}'.")

    def detect(self, frame, filter_class):
        res = self.model.predict(source=frame, verbose=False, conf=self.conf, iou=self.iou, classes=filter_class)[0]
        det = sv.Detections.from_ultralytics(res)
        return det, res
