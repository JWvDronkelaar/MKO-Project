import supervision as sv

class ByteTrackerWrapper:
    def __init__(self):
        self.bt = sv.ByteTrack()

    def update_with_detections(self, detections: sv.Detections):
        """Return the tracker object used previously in your script (tracks with .xyxy, .confidence, .tracker_id)."""
        tracks = self.bt.update_with_detections(detections)
        return tracks
