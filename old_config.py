# Source
CAM_INDEX = "Footage/People walking.mp4"
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
H_PATH = "homography/H.npy"
JSONL_PATH = "tracks.jsonl"

# Model
MODEL_PATH = "models/yolov8n.engine"
CONF_THRES = 0.1
IOU_THRES = 0.5
PERSON_CLS = 0
EMA_ALPHA = 0.6

# Options
SAVE_JSONL = False
SHOW_WINDOW = True
USE_HOMOGRAPHY = True

# Connection
HOST = "127.0.0.1"
PORT = 9999
