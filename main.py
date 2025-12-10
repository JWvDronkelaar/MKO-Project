import time
import json
import math
import cv2
import numpy as np

from config import *
from datatypes.datatype import BBox, WorldPosition
from video.video_capture import VideoSource
from detection.detector import PeopleDetector
from tracking.tracker import ByteTrackerWrapper
from transform.projection import Projector
from filters.smoothing import EMASmoother
from streamdata.messaging import UDPSender
import streamdata.jsonpack as jsonpack
from viz.visualizer import draw_frame
from viz.fps_tracker import FPSTracker

# optional JSONL logging
fout = open(JSONL_PATH, "w") if SAVE_JSONL else None

def main():
    print("[INFO] Starting refactored live tracker.")
    source = VideoSource(CAM_INDEX, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    detector = PeopleDetector(MODEL_PATH, conf=CONF_THRES, iou=IOU_THRES)
    tracker = ByteTrackerWrapper()
    projector = Projector(H_PATH, use_homography=USE_HOMOGRAPHY)
    smoother = EMASmoother(EMA_ALPHA)
    sender = UDPSender(HOST, PORT)

    _fps_tracker = FPSTracker()

    try:
        for frame, frame_number in source:
            ts = time.time()
            ts_str = time.strftime("%H:%M:%S")
            # 1) detect
            det, res = detector.detect(frame)
            # filter persons only if names mapping available
            if hasattr(res, "names") and isinstance(res.names, dict):
                cls = det.class_id if det.class_id is not None else []
                mask = []
                for c in cls:
                    mask.append(c == PERSON_CLS)
                if len(mask) > 0:
                    det = det[np.array(mask, dtype=bool)]

            # 2) tracking
            tracks = tracker.update_with_detections(det)

            # 3) process tracks into world positions
            world_positions = []
            # tracks exposes .xyxy, .confidence, .tracker_id (same as original script)
            for i, xyxy in enumerate(getattr(tracks, "xyxy", [])):
                conf = float(tracks.confidence[i]) if getattr(tracks, "confidence", None) is not None else 0.0
                track_id = int(tracks.tracker_id[i])
                x1, y1, x2, y2 = xyxy.astype(int)
                foot_x = (x1 + x2) // 2
                foot_y = y2

                # px -> world (meters or pixel fallback)
                X_world, Y_world = projector.to_world(foot_x, foot_y)

                # smoothing + speed/direction
                Xs, Ys, speed, direction = smoother.update(track_id, X_world, Y_world, ts)

                # wp = WorldPosition(id=track_id, x=Xs, y=Ys, r=direction, conf=conf)
                wp = WorldPosition(id=track_id, x=X_world, y=Y_world, r=0, conf=conf)
                world_positions.append(wp)

            # 4) produce packets
            packet = jsonpack.format_live_packet(world_positions, ts_str)
            packet_for_receiver = jsonpack.format_for_receiver(packet)

            # 5) output
            line = json.dumps(packet)
            print(line, flush=True)
            if fout:
                fout.write(line + "\n")

            print(f"[DEBUG] Sending data to UDP {HOST}:{PORT}")
            sender.send(packet_for_receiver)

            # 6) visualization
            if SHOW_WINDOW:
                vis = draw_frame(frame, tracks, show_tracker_count=True, fps_tracker=_fps_tracker)
                cv2.imshow("Live Position Tracker (ESC to quit)", vis)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    finally:
        print("[INFO] Shutting down.")
        source.release()
        cv2.destroyAllWindows()
        if fout:
            fout.close()

if __name__ == "__main__":
    main()
