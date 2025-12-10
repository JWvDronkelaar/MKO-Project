import socket
import json
from typing import Any

class UDPSender:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, obj: Any):
        """Sends object as JSON string via UDP."""
        payload = json.dumps(obj).encode("utf-8")
        self.sock.sendto(payload, (self.host, self.port))
