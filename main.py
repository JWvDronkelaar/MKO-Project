import time
import json
import cv2
import numpy as np

from config.settings import AppSettings
from datatypes.datatype import WorldPosition
from framesource.source import VideoFileSource, CameraSource
from framesource.FramePacer import FramePacer
from detection.detector import PeopleDetector
from tracking.tracker import ByteTrackerWrapper
from transform.projection import Projector
from transform.world_position_mapper import WorldPositionMapper
from filters.smoothing import EMASmoother
from streamdata.messaging import UDPSender
import streamdata.jsonpack as jsonpack
from viz.visualizer import draw_frame
from viz.fps_tracker import FPSTracker


class LiveTracker:
    def __init__(self, settings: AppSettings):
        self.settings = settings

        self.source = CameraSource(settings.video)

        self.detector = PeopleDetector(settings.yolo)
        self.tracker = ByteTrackerWrapper()
        self.projector = Projector(settings.tracking)
        self.smoother = EMASmoother(settings.tracking.ema_alpha)
        self.mapper = WorldPositionMapper(self.projector, self.smoother)
        self.sender = UDPSender(settings.network)

        self.pacer = FramePacer(settings.video.target_fps)

        self.fps_tracker = FPSTracker()

        self.running = False

        # optional JSONL logging
        self.fout = open(settings.jsonl_path, "w") if getattr(settings, "save_jsonl", False) else None


    def start(self):
        if self.running:
            print("[WARN] LiveTracker.start() called while already running.")
            return

        print("Starting Tracker!")
        print("Press ESC to quit...")
        print(f"[DEBUG] Sending data to UDP {self.settings.network.host}:{self.settings.network.port}")

        self.source.start()
        # Wait until the first frame arrives (spin-up)
        for i in range(5):
            if self.source.is_alive:
                print("Source is providing frames...")
                break
            if i == 4 and not self.source.is_alive:
                raise ValueError("Source did not initialize properly...")
            time.sleep(1)

        self.running = True
        try:
            self._run_loop()
        finally:
            # Make sure we stop everything if start() returns unexpectedly
            self.stop()

    def stop(self):
        if not self.running:
            return
        self.running = False


    def _run_loop(self):
        try:
            self.fps_tracker.update()
            
            while self.running:
                # If the source thread stopped (e.g. file EOF), exit loop
                if not self.source.is_alive:
                    break

                with self.pacer as should_process:
                    if not should_process:
                        continue # skip this frame
                    
                    frame, frame_number = self.source.read()
                    loop_start = time.time()

                    # 1) detection (YOLO)
                    det, res = self.detector.detect(frame, filter_class = [settings.yolo.person_class_id])

                    # 2) tracking (ByteTrack)
                    tracks = self.tracker.update_with_detections(det)

                    # 3) world positions (projection + smoothing)
                    world_positions = self.mapper.map_tracks(tracks, loop_start)

                    # 4) JSON payloads
                    packet = jsonpack.format_live_packet(world_positions, time.strftime("%H:%M:%S"))
                    packet_for_receiver = jsonpack.format_for_receiver(packet)

                    # 5) send via UDP
                    try:
                        self.sender.send(packet_for_receiver)
                    except Exception as e:
                        # do not crash the loop on transient network errors
                        print(f"[WARN] UDP send failed: {e}")

                    # 6) optional logging
                    if self.fout:
                        try:
                            self.fout.write(json.dumps(packet) + "\n")
                        except Exception:
                            pass

                    # 7) visualization
                    if getattr(self.settings, "visualizer", None) and getattr(self.settings.visualizer, "show_window", False):
                        vis = draw_frame(frame, tracks, self.settings.visualizer, fps_tracker=self.fps_tracker)
                        cv2.imshow("Live Position Tracker (ESC to quit)", vis)
                        key = cv2.waitKey(1)
                    else:
                        # still poll for ESC even if window not shown
                        key = cv2.waitKey(1)

                    if key == 27:  # ESC
                        self.running = False
                        break

                    self.fps_tracker.update()
        finally:
            self._cleanup()


    def _cleanup(self):
        print("[INFO] Shutting down.")
        try:
            self.source.stop()
        except Exception:
            pass

        # destroy windows
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        # close log
        if self.fout:
            try:
                self.fout.close()
            except Exception:
                pass
            self.fout = None

        # close UDP sender if it provides a close() method
        try:
            if hasattr(self.sender, "close"):
                try:
                    self.sender.close()
                except Exception:
                    pass
        except Exception:
            pass


# Optional quick-run guard
if __name__ == "__main__":
    settings = AppSettings()
    # inject VideoFileSource(settings.video) or CameraSource(settings.video)
    tracker = LiveTracker(settings)
    tracker.start()
