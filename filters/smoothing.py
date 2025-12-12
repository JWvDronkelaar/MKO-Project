import math
from typing import Dict, Tuple
import numpy as np


class KalmanSmoother:
    """
    A per-ID 2D position+velocity Kalman filter.
    State vector:
        [x, y, vx, vy]^T
    """

    def __init__(self):
        self.filters: Dict[int, Dict[str, np.ndarray]] = {}  # id → KF state

    def _init_filter(self, x: float, y: float, t: float):
        """Initializes a Kalman filter for a new track."""
        kf = {}

        # State vector (x, y, vx, vy)
        kf["x"] = np.array([[x], [y], [0.0], [0.0]], dtype=float)

        # State covariance matrix
        kf["P"] = np.eye(4) * 100.0  # high uncertainty initially

        # Measurement matrix: we only observe x,y
        kf["H"] = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=float)

        # Measurement noise
        kf["R"] = np.eye(2) * 10.0

        # Process noise (adjust if needed)
        kf["Q_base"] = np.array([
            [1, 0, 0,   0],
            [0, 1, 0,   0],
            [0, 0, 10,  0],
            [0, 0, 0,  10],
        ], dtype=float)

        kf["last_t"] = t
        return kf

    def update(self, track_id: int, x: float, y: float, t: float) -> Tuple[float, float, float, float]:
        """
        Performs a Kalman prediction+update for a position measurement.
        Returns:
            smoothed_x, smoothed_y, speed, direction(deg)
        """
        if track_id not in self.filters:
            self.filters[track_id] = self._init_filter(x, y, t)
            return x, y, 0.0, 0.0

        kf = self.filters[track_id]

        # Time step
        dt = t - kf["last_t"]
        if dt <= 0:
            # No time passed — return last state but update time
            state = kf["x"]
            vx, vy = state[2, 0], state[3, 0]
            speed = math.hypot(vx, vy)
            direction = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0
            kf["last_t"] = t
            return state[0, 0], state[1, 0], speed, direction

        kf["last_t"] = t

        # ----------------------------------------------------
        # 1) PREDICTION STEP
        # ----------------------------------------------------
        # State transition matrix
        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1],
        ], dtype=float)

        x_pred = F @ kf["x"]
        P_pred = F @ kf["P"] @ F.T + kf["Q_base"]

        # ----------------------------------------------------
        # 2) UPDATE STEP (measurement = x,y)
        # ----------------------------------------------------
        z = np.array([[x], [y]], dtype=float)
        H = kf["H"]

        y_residual = z - H @ x_pred
        S = H @ P_pred @ H.T + kf["R"]
        K = P_pred @ H.T @ np.linalg.inv(S)

        x_new = x_pred + K @ y_residual
        P_new = (np.eye(4) - K @ H) @ P_pred

        # ----------------------------------------------------
        # 3) STORE UPDATED STATE
        # ----------------------------------------------------
        kf["x"] = x_new
        kf["P"] = P_new

        # Extract smoothed state
        Xs = x_new[0, 0]
        Ys = x_new[1, 0]
        vx = x_new[2, 0]
        vy = x_new[3, 0]

        speed = math.hypot(vx, vy)
        direction = (math.degrees(math.atan2(vy, vx)) + 360.0) % 360.0

        return Xs, Ys, speed, direction
