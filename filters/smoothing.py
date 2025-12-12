import math
import numpy as np
from typing import Dict, Tuple


class KalmanSmoother:
    """
    A 2D Kalman filter with direction stabilization.
    State: [x, y, vx, vy]
    """

    def __init__(self, movement_threshold: float = 0.3):
        # Below this speed we consider the person "stationary"
        self.movement_threshold = movement_threshold
        self.filters: Dict[int, Dict[str, np.ndarray]] = {}
        self.last_direction: Dict[int, float] = {}  # stored per track

    def _init_filter(self, x: float, y: float, t: float):
        kf = {}
        kf["x"] = np.array([[x], [y], [0.0], [0.0]], dtype=float)
        kf["P"] = np.eye(4) * 100.0
        kf["H"] = np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0]], dtype=float)
        kf["R"] = np.eye(2) * 10.0
        kf["Q_base"] = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 10, 0],
                                 [0, 0, 0, 10]], dtype=float)
        kf["last_t"] = t
        return kf

    def update(self, track_id: int, x: float, y: float, t: float) -> Tuple[float, float, float, float]:
        """
        Returns smoothed_x, smoothed_y, speed, direction(deg)
        """

        # ----------------------------------------------------
        # Initialize new track
        # ----------------------------------------------------
        if track_id not in self.filters:
            self.filters[track_id] = self._init_filter(x, y, t)
            self.last_direction[track_id] = 0.0
            return x, y, 0.0, 0.0

        kf = self.filters[track_id]

        # ----------------------------------------------------
        # Compute dt
        # ----------------------------------------------------
        dt = t - kf["last_t"]
        if dt <= 0:
            state = kf["x"]
            vx, vy = state[2, 0], state[3, 0]
            speed = math.hypot(vx, vy)
            direction = self.last_direction[track_id]
            return state[0, 0], state[1, 0], speed, direction

        kf["last_t"] = t

        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------
        F = np.array([[1, 0, dt, 0],
                      [0, 1, 0, dt],
                      [0, 0, 1,  0],
                      [0, 0, 0,  1]], dtype=float)

        x_pred = F @ kf["x"]
        P_pred = F @ kf["P"] @ F.T + kf["Q_base"]

        # ----------------------------------------------------
        # UPDATE (x, y)
        # ----------------------------------------------------
        z = np.array([[x], [y]], dtype=float)
        H = kf["H"]

        y_residual = z - H @ x_pred
        S = H @ P_pred @ H.T + kf["R"]
        K = P_pred @ H.T @ np.linalg.inv(S)

        x_new = x_pred + K @ y_residual
        P_new = (np.eye(4) - K @ H) @ P_pred

        kf["x"] = x_new
        kf["P"] = P_new

        # ----------------------------------------------------
        # COMPUTE OUTPUT
        # ----------------------------------------------------
        Xs = x_new[0, 0]
        Ys = x_new[1, 0]
        vx = x_new[2, 0]
        vy = x_new[3, 0]

        speed = math.hypot(vx, vy)

        # ----------------------------------------------------
        # DIRECTION STABILIZATION
        # ----------------------------------------------------
        if speed < self.movement_threshold:
            # Object is basically stationary → freeze direction
            direction = self.last_direction[track_id]
        else:
            # Compute new direction from velocity
            direction = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
            self.last_direction[track_id] = direction

        return Xs, Ys, speed, direction
