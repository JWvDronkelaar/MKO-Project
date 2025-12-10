import numpy as np

class ColorPalette:
    def __init__(self):
        hexes = [
            "#E6194B", "#3CB44B", "#FFE119", "#0082C8", "#F58231",
            "#911EB4", "#46F0F0", "#F032E6", "#D2F53C", "#008080",
            "#AA6E28", "#800000", "#808000", "#000080", "#808080"
        ]
        self.colors = [self._hex_to_bgr(h) for h in hexes]

    def _hex_to_bgr(self, h):
        h = h.lstrip('#')
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return (b, g, r)

    def by_idx(self, idx: int):
        return self.colors[idx % len(self.colors)]
