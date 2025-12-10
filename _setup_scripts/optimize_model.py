from ultralytics import YOLO
from config import *

# Load the YOLO11 model
model = YOLO(MODEL_PATH)

# Export the model to TensorRT format
model.export(format="engine")
