from dataclasses import dataclass, field
from typing import Optional

@dataclass
class YOLOSettings:
    model_path: str = "Algos/yolov8n.pt"
    conf_threshold: float = 0.1
    iou_threshold: float = 0.5
    person_class_id: int = 0
    use_gpu: bool = True


@dataclass
class TrackingSettings:
    ema_alpha: float = 0.9  # default = 0.6
    use_homography: bool = True
    homography_path: str = "homography/H.npy"


@dataclass
class VideoSettings:
    # camera_index: str = "Footage/People walking.mp4"
    # width: int = 1280
    # height: int = 720
    camera_index: int = 2
    width: int = 1920
    height: int = 1080
    

@dataclass
class Visualizer:
    show_window: bool = True
    show_tracker_count: bool = True
    show_fps: bool = True


@dataclass
class NetworkSettings:
    host: str = "127.0.0.1"
    port: int = 9999


@dataclass
class AppSettings:
    yolo: YOLOSettings = field(default_factory=YOLOSettings)
    tracking: TrackingSettings = field(default_factory=TrackingSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    visualizer: VideoSettings = field(default_factory=Visualizer)
    network: NetworkSettings = field(default_factory=NetworkSettings)

    save_jsonl: bool = False
    jsonl_path: str = "tracks.jsonl"
