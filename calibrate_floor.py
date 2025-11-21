# calibrate_floor.py
import cv2, numpy as np

CAM_INDEX = "People walking.mp4"
SAVE_PATH = "H.npy"   # homografie wordt hier opgeslagen

clicked = []

def mouse_cb(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(clicked)<4:
        clicked.append((x,y))
        print(f"Pixelpunt {len(clicked)}: {(x,y)}")

cap = cv2.VideoCapture(CAM_INDEX)
cv2.namedWindow("Klik 4 vloerpunten (ESC als klaar)")
cv2.setMouseCallback("Klik 4 vloerpunten (ESC als klaar)", mouse_cb)

print(">> Klik 4 vloerpunten in volgorde (bijv. linksonder, rechtsonder, rechtsboven, linksboven).")
print(">> Daarna vraagt het script om de bijbehorende 4 (X,Y)-meters.")
while True:
    ok, frame = cap.read()
    if not ok: break
    vis = frame.copy()
    for i,(x,y) in enumerate(clicked):
        cv2.circle(vis,(x,y),6,(0,255,255),-1)
        cv2.putText(vis,str(i+1),(x+8,y-8),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)
    cv2.imshow("Klik 4 vloerpunten (ESC als klaar)", vis)
    key = cv2.waitKey(80) & 0xFF
    if key == 27 and len(clicked)==4:
        break
    

cap.release()
cv2.destroyAllWindows()

if len(clicked)!=4:
    raise SystemExit("Niet genoeg punten geklikt (4 nodig).")

print("\nVoer nu de 4 overeenkomstige VLOER-coördinaten (in meters) in **dezelfde volgorde** in.")
floor_pts = []
for i in range(4):
    X = float(input(f"Vloer X{i+1} (m): "))
    Y = float(input(f"Vloer Y{i+1} (m): "))
    floor_pts.append([X,Y])

# maak 2D → 2D homografie (pixels → meters)
px = np.array(clicked, dtype=np.float32)
wr = np.array(floor_pts, dtype=np.float32)

H, mask = cv2.findHomography(px, wr, method=cv2.RANSAC)
np.save(SAVE_PATH, H)
print(f"\n✅ Homografie opgeslagen naar {SAVE_PATH}")
