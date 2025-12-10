from typing import List, Dict
from datatypes.datatype import WorldPosition

def format_live_packet(world_positions: List[WorldPosition], ts_str: str) -> Dict:
    """Return the same packet structure your original script printed."""
    people = []
    for p in world_positions:
        people.append({
            "id": int(p.id),
            "pos": [round(p.x, 3), round(p.y, 3)],
            "dir_deg": round(p.r, 1),
            "conf": round(p.conf, 2)
        })
    return {"ts": ts_str, "people": people}

def format_for_receiver(packet: Dict) -> List[Dict]:
    """Format packet to consumer (Unity/Blender) - same as your legacy format_live_packet."""
    out = []
    for p in packet.get("people", []):
        x, y = p["pos"]
        r = p["dir_deg"]
        out.append({
            "id": int(p["id"]),
            "x": float(x),
            "y": float(y),
            "z": 0.0,
            "r": float(r)
        })
    return out
