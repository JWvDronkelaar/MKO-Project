from typing import List

import cv2

from .palette import ColorPalette
from datatypes.datatype import WorldPosition

palette = ColorPalette()


def draw_frame(frame, tracks, world_positions: List[WorldPosition], fps_tracker = None, show_tracker_count=True):
    vis = frame.copy()
    # draw tracked bboxes and foot positions (tracks expected to have xyxy, confidence, tracker_id)
    if tracks is not None:
        for i, xyxy in enumerate(getattr(tracks, "xyxy", [])):
            x1, y1, x2, y2 = xyxy.astype(int)
            conf = float(tracks.confidence[i]) if getattr(tracks, "confidence", None) is not None else 0.0
            tid = int(tracks.tracker_id[i])
            color = palette.by_idx(tid)
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            foot_x = (x1 + x2) // 2
            foot_y = y2
            cv2.circle(vis, (foot_x, foot_y), 5, color, -1)
            cv2.putText(vis, f"ID {tid} | {round(conf,2)}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # TODO: make "draw_positions_list" argument or better yet, configuration to be passed along to visualizer
    if True:
        draw_positions_list(vis, world_positions)

    if show_tracker_count:
        cv2.putText(vis, f"People: {len(world_positions)}", (12,28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    
    if fps_tracker is not None:
        draw_fps(vis, fps_tracker)
    
    return vis


def draw_positions_list(vis, world_positions):
    for p in world_positions:
        px = 12
        py = 40 + 18 * p.id
        cv2.putText(vis, f"WP ID {p.id}: ({p.x:.2f},{p.y:.2f}) r={p.r:.1f}", (px, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)


def draw_fps(vis, fps_tracker):
    fps_tracker.update()

    h, w = vis.shape[:2]
    x = w - 260
    y = 20

    cv2.putText(vis, f"FPS: {fps_tracker.current:5.1f}", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(vis, f"AVG: {fps_tracker.average:5.1f}", (x, y+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.putText(vis, f"MIN: {fps_tracker.minimum:5.1f}", (x, y+40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.putText(vis, f"MAX: {fps_tracker.maximum:5.1f}", (x, y+60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)
