import time
import json
import math
import cv2
import numpy as np

from config.settings import AppSettings
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

settings = AppSettings()

# optional JSONL logging
fout = open(settings.jsonl_path, "w") if settings.save_jsonl else None

def main():
    source = VideoSource(settings.video)
    detector = PeopleDetector(settings.yolo)
    tracker = ByteTrackerWrapper()
    projector = Projector(settings.tracking)
    smoother = EMASmoother(settings.tracking.ema_alpha)
    sender = UDPSender(settings.network)

    _fps_tracker = FPSTracker()

    print("Starting Tracker!")
    print(f"[DEBUG] Sending data to UDP {settings.network.host}:{settings.network.port}")
    # TODO: echo all settings here?

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
                    mask.append(c == settings.yolo.person_class_id)
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
            # TODO: why is packet for receiver (which is not optional), dependant on packet
            # which is optional for logging?
            packet = jsonpack.format_live_packet(world_positions, ts_str)
            packet_for_receiver = jsonpack.format_for_receiver(packet)

            # 5) output
            sender.send(packet_for_receiver)

            # TODO: create levels for logging, this is a lot of spam eating up more important messages
            line = json.dumps(packet)
            print(line, flush=True)
            if fout:
                fout.write(line + "\n")

            # 6) visualization
            if settings.visualizer.show_window:
                vis = draw_frame(frame, tracks, settings.visualizer, fps_tracker=_fps_tracker)
                cv2.imshow("Live Position Tracker (ESC to quit)", vis)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    finally:
        print("[INFO] Shutting down.")
        source.release()
        cv2.destroyAllWindows()
        # TODO: does the socket not need to be closed?
        
        # TODO: this is json out I think, seperate this logic out completely
        if fout:
            fout.close()

if __name__ == "__main__":
    main()
