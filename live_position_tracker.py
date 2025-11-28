# live_position_tracker.py
import time, json, math, sys
import cv2, numpy as np
from ultralytics import YOLO
import supervision as sv

# external_server.py
import socket
import time
import json
import math

# Hosting settings
HOST = "127.0.0.1"
PORT = 9999

# ---------- Settings ----------
CAM_INDEX = "Footage/People walking.mp4"
MODEL = "yolov8n.pt"     # mensen-detectie; CPU ok
CONF_THRES = 0.1
IOU_THRES = 0.5
SAVE_JSONL = True
JSONL_PATH = "tracks.jsonl"
H_PATH = "H.npy"         # van calibrate_floor.py
USE_HOMOGRAPHY = True
EMA_ALPHA = 0.6          # smoothing per ID
SHOW_WINDOW = False
PERSON_CLS = 0           # klasse-id voor "person" in COCO is 0
# ------------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# laad homografie
try:
    H = np.load(H_PATH)
except FileNotFoundError:
    H = None
    print("[WARN] Geen H.npy gevonden — homografie uitgeschakeld.")

def px_to_m(x_px, y_px):
    if USE_HOMOGRAPHY and H is not None:
        pt = np.array([[x_px, y_px]], dtype=np.float32)
        pt = cv2.perspectiveTransform(pt.reshape(1,1,2), H).reshape(2)
        return float(pt[0]), float(pt[1])
    else:
        # geen homografie → gewoon pixelwaarden teruggeven
        return float(x_px), float(y_px)

# tracker
byte_tracker = sv.ByteTrack()

# smoothing cache & vorige meting
state = {}  # id -> {"x":X, "y":Y, "t":ts}
def ema(prev, cur, a=EMA_ALPHA):
    return a*prev + (1-a)*cur if prev is not None else cur

# logger
fout = open(JSONL_PATH,"w") if SAVE_JSONL else None

# yolo
model = YOLO(MODEL)
cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

palette = sv.ColorPalette.from_hex([
    "#E6194B", "#3CB44B", "#FFE119", "#0082C8", "#F58231",
    "#911EB4", "#46F0F0", "#F032E6", "#D2F53C", "#008080",
    "#AA6E28", "#800000", "#808000", "#000080", "#808080"
])

print("[INFO] Live positie-tracking gestart. Druk ESC om te stoppen.")
try:
    while True:
        ok, frame = cap.read()
        if not ok: break
        ts = time.time()
        ts2 = time.strftime("%H:%M:%S")

        # 1) detect
        res = model.predict(source=frame, verbose=False, conf=CONF_THRES, iou=IOU_THRES)[0]
        det = sv.Detections.from_ultralytics(res)
        # filter alleen 'person'
        if res.names and isinstance(res.names, dict):
            cls = det.class_id if det.class_id is not None else []
            mask = np.array([c == PERSON_CLS for c in cls], dtype=bool)
            det = det[mask]

        # 2) track (stabiele IDs)
        tracks = byte_tracker.update_with_detections(det)

        people_out = []
        vis = frame.copy()

        for i,xyxy in enumerate(tracks.xyxy):
            conf = float(tracks.confidence[i]) if tracks.confidence is not None else None
            # if conf is None or conf < 0.75:
            #    continue
            track_id = int(tracks.tracker_id[i])
            x1,y1,x2,y2 = xyxy.astype(int)
            # 3) voetpunt (midden onder bbox)
            foot_x = (x1 + x2)//2
            foot_y = y2

            # 4) px -> meters
            X, Y = px_to_m(foot_x, foot_y)

            # 5) smoothing + snelheid/richting
            prev = state.get(track_id)
            if prev:
                # EMA pos
                Xs = ema(prev["x"], X)
                Ys = ema(prev["y"], Y)
                dt = max(1e-6, ts - prev["t"])
                vx = (Xs - prev["x"])/dt
                vy = (Ys - prev["y"])/dt
            else:
                Xs, Ys = X, Y
                vx, vy = 0.0, 0.0
            

            speed = math.hypot(vx, vy)
            direction = (math.degrees(math.atan2(vy, vx)) + 360) % 360
            state[track_id] = {"x": Xs, "y": Ys, "t": ts}

            people_out.append({
                "id": track_id,
                "pos": [round(Xs,3), round(Ys,3)],
            #    "speed_m_s": round(speed,3),
                "dir_deg": round(direction,1),
                "conf": round(conf, 2)
            })

            # viz
            color = palette.by_idx(track_id).as_bgr()
            cv2.rectangle(vis,(x1,y1),(x2,y2),color,2)
            cv2.circle(vis,(foot_x,foot_y),5,color,-1)
            cv2.putText(vis,f"ID {track_id} | {round(conf, 2)} | {round(Xs,2), round(Ys,2)}| {round(direction,1)} ",(x1,y1-8),cv2.FONT_HERSHEY_SIMPLEX,0.6,color,2)
            
        
        # 6) live JSON (stdout + optioneel log)
        packet = {"ts": ts2, "people": people_out}
        line = json.dumps(packet)
        print(line, flush=True)
        if fout: fout.write(line+"\n")

        def format_live_packet(packet):
            """Zet inkomende tracker-data om naar Blender/Unity formaat."""
            out = []
            people = packet.get("people", [])

            for p in people:
                x, y = p["pos"]
                r = p["dir_deg"]
                out.append({
                    "id": str(p["id"]),
                    "x": float(x),
                    "y": float(y),
                    "z": 0.0,
                    "r": float(r)
                })

            return out

        # 7) send via UDP 
        print(f"Sending data to UDP {HOST}:{PORT}")
        sock.sendto(json.dumps(format_live_packet(packet)).encode("utf-8"), (HOST, PORT))

        if SHOW_WINDOW:
            cv2.putText(vis,f"People: {len(people_out)}",(12,28),
                        cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
            cv2.imshow("Live Position Tracker (ESC to quit)", vis)
            if cv2.waitKey(1) & 0xFF == 27:
                break


finally:
    cap.release()
    cv2.destroyAllWindows()
    if fout: fout.close()
