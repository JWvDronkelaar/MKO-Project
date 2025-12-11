from typing import List
from datatypes.datatype import WorldPosition, BBox
from transform.projection import Projector
from filters.smoothing import EMASmoother

class WorldPositionMapper:
    """
    Converts tracked bounding boxes to world coordinates with smoothing.
    """

    def __init__(self, projector: Projector, smoother: EMASmoother):
        self.projector = projector
        self.smoother = smoother

    def map_tracks(self, tracks, timestamp: float) -> List[WorldPosition]:
        """
        Convert tracked bounding boxes into smoothed world positions.

        Args:
            tracks: tracker object exposing .xyxy, .confidence, .tracker_id
            timestamp: current time in seconds

        Returns:
            List[WorldPosition]
        """
        world_positions = []

        for i, xyxy in enumerate(getattr(tracks, "xyxy", [])):
            try:
                conf = float(tracks.confidence[i]) if getattr(tracks, "confidence", None) is not None else 0.0
                track_id = int(tracks.tracker_id[i])

                x1, y1, x2, y2 = xyxy.astype(int)
                foot_x = (x1 + x2) // 2
                foot_y = y2

                # px -> world
                x_world, y_world = self.projector.to_world(foot_x, foot_y)

                # smoothing + speed/direction
                x_smoothed, y_smoothed, speed, direction = self.smoother.update(track_id, x_world, y_world, timestamp)

                wp = WorldPosition(
                    id=track_id,
                    x=x_smoothed,
                    y=y_smoothed,
                    r=direction,
                    conf=conf
                )

                world_positions.append(wp)

            except Exception as e:
                print(f"[ERROR] Failed processing track {i}: {e}")

        return world_positions
