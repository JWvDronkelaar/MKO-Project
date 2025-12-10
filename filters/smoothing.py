import math
from typing import Dict, Tuple

class EMASmoother:
    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha
        self.state: Dict[int, Dict[str,float]] = {}  # id -> {"x":..., "y":..., "t":...}

    def _ema(self, prev, cur):
        return self.alpha * prev + (1.0 - self.alpha) * cur

    def update(self, track_id: int, x: float, y: float, t: float) -> Tuple[float, float, float, float]:
        prev = self.state.get(track_id)
        if prev:
            Xs = self._ema(prev["x"], x)
            Ys = self._ema(prev["y"], y)
            dt = max(1e-6, t - prev["t"])
            vx = (Xs - prev["x"]) / dt
            vy = (Ys - prev["y"]) / dt
        else:
            Xs, Ys = x, y
            vx, vy = 0.0, 0.0

        speed = math.hypot(vx, vy)
        direction = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
        self.state[track_id] = {"x": Xs, "y": Ys, "t": t}
        return Xs, Ys, speed, direction
