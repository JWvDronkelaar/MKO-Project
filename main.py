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


class LiveTracker:
    def __init__(self, settings: AppSettings):
        self.settings = settings

        # components
        self.source = VideoSource(settings.video)
        self.detector = PeopleDetector(settings.yolo)
        self.tracker = ByteTrackerWrapper()
        self.projector = Projector(settings.tracking)
        self.smoother = EMASmoother(settings.tracking.ema_alpha)
        self.sender = UDPSender(settings.network)
        self.fps_tracker = FPSTracker()

        # state
        self.running = False
        self.frame_number = 0

        # optional JSONL logging
        self.fout = open(settings.jsonl_path, "w") if settings.save_jsonl else None


    def start(self):
        if self.running:
            print("[WARN] LiveTracker.start() called while already running.")
            return

        self.running = True
        print("Starting Tracker!")
        print("Press ESC to quit...")
        print(f"[DEBUG] Sending data to UDP {self.settings.network.host}:{self.settings.network.port}")

        self._run_loop()

    def stop(self):
        if not self.running:
            return
        self.running = False


    def _run_loop(self):
        try:
            for frame, frame_number in self.source:
                if not self.running:
                    break

                ts = time.time()
                ts_str = time.strftime("%H:%M:%S")

                # 1) detection
                det, res = self.detector.detect(frame)

                # filter persons only
                if hasattr(res, "names") and isinstance(res.names, dict):
                    cls = det.class_id if det.class_id is not None else []
                    mask = [(c == self.settings.yolo.person_class_id) for c in cls]
                    if mask:
                        det = det[np.array(mask, dtype=bool)]

                # 2) ByteTrack tracking
                tracks = self.tracker.update_with_detections(det)

                # 3) Convert to world positions
                world_positions = self._produce_world_positions(tracks, ts)

                # 4) JSON packaging
                packet = jsonpack.format_live_packet(world_positions, ts_str)
                packet_for_receiver = jsonpack.format_for_receiver(packet)

                # 5) Send via UDP
                self.sender.send(packet_for_receiver)

                # logging (very verbose)
                line = json.dumps(packet)
                print(line, flush=True)
                if self.fout:
                    self.fout.write(line + "\n")

                # 6) Visualization
                if self.settings.visualizer.show_window:
                    vis = draw_frame(
                        frame,
                        tracks,
                        self.settings.visualizer,
                        fps_tracker=self.fps_tracker
                    )

                    cv2.imshow("Live Position Tracker (ESC to quit)", vis)
                    key = cv2.waitKey(1) & 0xFF == 27
                else:
                    # still poll for ESC even though no window is shown
                    key = cv2.waitKey(1) & 0xFF == 27
                
                if key == 27:
                    self._running = False # Could be used outside of this loop and if it is, it serves a purpose. Check if it can be removed.
                    break

                self.frame_number += 1

        finally:
            self._cleanup()


    def _produce_world_positions(self, tracks, ts: float):
        """Convert tracked bounding boxes into world coordinates with smoothing."""
        world_positions = []

        for i, xyxy in enumerate(getattr(tracks, "xyxy", [])):
            conf = float(tracks.confidence[i]) if getattr(tracks, "confidence", None) is not None else 0.0
            track_id = int(tracks.tracker_id[i])

            x1, y1, x2, y2 = xyxy.astype(int)
            foot_x = (x1 + x2) // 2
            foot_y = y2

            # px -> world
            x_world, y_world = self.projector.to_world(foot_x, foot_y)

            # smoothing + speed/direction
            x_smoothed, y_smoothed, speed, direction = self.smoother.update(track_id, x_world, y_world, ts)

            # BUG/NOTE: original code overwrote smoothed values with raw world coords.
            wp = WorldPosition(
                id=track_id,
                x=x_smoothed,
                y=y_smoothed,
                r=0,           # direction was removed in your version
                conf=conf
            )

            world_positions.append(wp)

        return world_positions


    def _cleanup(self):
        print("[INFO] Shutting down.")

        try:
            self.source.release()
        except Exception:
            pass

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        if self.fout:
            self.fout.close()
            self.fout = None

        # TODO: Does the UDP socket need to be closed? (Your original code had the same TODO)
        # sender.close() could be implemented if needed.


# TODO: remove for final
if __name__ == "__main__":
    settings = AppSettings()
    tracker = LiveTracker(settings)
    tracker.start()
