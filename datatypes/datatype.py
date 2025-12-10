from dataclasses import dataclass
from typing import Tuple

@dataclass
class BBox:
    x1: int
    y1: int
    x2: int
    y2: int
    conf: float
    cls: int = None

    def foot(self) -> Tuple[int,int]:
        return ((self.x1 + self.x2) // 2, self.y2)

@dataclass
class WorldPosition:
    id: int
    x: float
    y: float
    r: float
    conf: float
