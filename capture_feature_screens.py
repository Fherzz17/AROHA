"""Capture AROHA's single-page views through the local Chrome DevTools protocol."""
import base64
import hashlib
import json
import os
import socket
import struct
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "report" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

def ws_connect(url):
    host_port, path = url.removeprefix("ws://").split("/", 1)
    host, port = host_port.split(":")
    sock = socket.create_connection((host, int(port)), timeout=15)
    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        f"GET /{path} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\n"
        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(request.encode())
    if b"101" not in sock.recv(4096):
        raise RuntimeError("DevTools WebSocket handshake failed")
    return sock

def send_frame(sock, text):
    data = text.encode()
    mask = os.urandom(4)
    length = len(data)
    header = bytearray([0x81])
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.extend([0x80 | 126]); header.extend(struct.pack("!H", length))
    else:
        header.extend([0x80 | 127]); header.extend(struct.pack("!Q", length))
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    sock.sendall(bytes(header) + mask + masked)

def recv_exact(sock, size):
    buff = b""
    while len(buff) < size:
        chunk = sock.recv(size - len(buff))
        if not chunk: raise RuntimeError("DevTools connection closed")
        buff += chunk
    return buff

def recv_frame(sock):
    first, second = recv_exact(sock, 2)
    length = second & 0x7F
    if length == 126: length = struct.unpack("!H", recv_exact(sock, 2))[0]
    elif length == 127: length = struct.unpack("!Q", recv_exact(sock, 8))[0]
    masked = second & 0x80
    mask = recv_exact(sock, 4) if masked else b""
    payload = recv_exact(sock, length)
    if masked: payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return payload.decode(errors="replace")

class CDP:
    def __init__(self, url): self.sock, self.next = ws_connect(url), 0
    def call(self, method, params=None):
        self.next += 1; msg_id = self.next
        send_frame(self.sock, json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            response = json.loads(recv_frame(self.sock))
            if response.get("id") == msg_id:
                if "error" in response: raise RuntimeError(response["error"])
                return response.get("result", {})

def main():
    page_url = "http://127.0.0.1:8000/"
    req = Request("http://127.0.0.1:9223/json/new?" + quote(page_url, safe=":/"), method="PUT")
    page = json.loads(urlopen(req).read().decode())
    cdp = CDP(page["webSocketDebuggerUrl"])
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")
    cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
    time.sleep(2.5)
    views = [
        ("home", "01-home"), ("dashboard", "02-dashboard"), ("skills", "03-skill-search"),
        ("career", "04-career-explorer"), ("emerging", "05-emerging-skills"),
        ("recommend", "06-skill-gap-resume"), ("nlp", "07-nlp-analyzer"), ("about", "08-methodology"),
    ]
    for view, name in views:
        cdp.call("Runtime.evaluate", {"expression": f"switchView('{view}')"})
        time.sleep(1.4)
        image = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})["data"]
        (OUT / f"{name}.png").write_bytes(base64.b64decode(image))
        print(OUT / f"{name}.png")

if __name__ == "__main__": main()
