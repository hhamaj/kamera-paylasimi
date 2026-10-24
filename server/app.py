"""Kamera paylasim server'i.

- /ws/camera : client'lar baglanir. Ilk mesaj JSON {"name": "..."}, sonrasi binary JPEG kareleri.
- /ws/view   : tarayici baglanir. Server kamera listesini (JSON) ve kareleri (binary) gonderir.
  Binary mesaj formati: 4 byte big-endian kamera id + JPEG verisi.
- /          : Vue ile build edilmis web sitesi (static/).
"""

import argparse
import json
import struct
import threading
import time
from pathlib import Path

from flask import Flask, send_from_directory
from flask_sock import Sock
from simple_websocket import ConnectionClosed

STATIC_DIR = Path(__file__).parent / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
sock = Sock(app)


class Camera:
    def __init__(self, cam_id, name):
        self.id = cam_id
        self.name = name
        self.frame = None
        self.seq = 0


class Hub:
    """Bagli kameralari ve son karelerini tutar; yeni veri gelince izleyicileri uyandirir."""

    def __init__(self):
        self.cond = threading.Condition()
        self.cameras = {}
        self.next_id = 1
        self.version = 0  # kamera listesi her degistiginde artar

    def add(self, name):
        with self.cond:
            cam = Camera(self.next_id, name)
            self.next_id += 1
            self.cameras[cam.id] = cam
            self.version += 1
            self.cond.notify_all()
            return cam

    def remove(self, cam):
        with self.cond:
            self.cameras.pop(cam.id, None)
            self.version += 1
            self.cond.notify_all()

    def push_frame(self, cam, data):
        with self.cond:
            cam.frame = data
            cam.seq += 1
            self.cond.notify_all()

    def has_new_frames(self, sent_seq):
        return any(c.frame is not None and sent_seq.get(c.id) != c.seq for c in self.cameras.values())

    def camera_list(self):
        return [{"id": c.id, "name": c.name} for c in self.cameras.values()]


hub = Hub()


@sock.route("/ws/camera")
def camera_ws(ws):
    try:
        hello = json.loads(ws.receive(timeout=10))
        name = str(hello.get("name", "")).strip()[:64] or "Isimsiz kamera"
    except Exception:
        return

    cam = hub.add(name)
    print(f"[+] Kamera baglandi: {name} (id={cam.id})", flush=True)
    try:
        while True:
            data = ws.receive()
            if isinstance(data, (bytes, bytearray)):
                hub.push_frame(cam, bytes(data))
    except ConnectionClosed:
        pass
    finally:
        hub.remove(cam)
        print(f"[-] Kamera ayrildi: {name} (id={cam.id})", flush=True)


@sock.route("/ws/view")
def view_ws(ws):
    sent_version = -1
    sent_seq = {}
    try:
        while True:
            with hub.cond:
                hub.cond.wait_for(
                    lambda: hub.version != sent_version or hub.has_new_frames(sent_seq),
                    timeout=1.0,
                )
                version = hub.version
                cameras = hub.camera_list() if version != sent_version else None
                frames = [
                    (c.id, c.seq, c.frame)
                    for c in hub.cameras.values()
                    if c.frame is not None and sent_seq.get(c.id) != c.seq
                ]

            if cameras is not None:
                ws.send(json.dumps({"type": "cameras", "cameras": cameras}))
                sent_version = version
                live = {c["id"] for c in cameras}
                sent_seq = {k: v for k, v in sent_seq.items() if k in live}

            for cam_id, seq, frame in frames:
                ws.send(struct.pack(">I", cam_id) + frame)
                sent_seq[cam_id] = seq

            if not ws.connected:
                break
    except ConnectionClosed:
        pass


@app.route("/")
def index():
    if not (STATIC_DIR / "index.html").exists():
        return (
            "Web sitesi build edilmemis. 'web' klasorunde 'npm install && npm run build' calistirin.",
            500,
        )
    return send_from_directory(STATIC_DIR, "index.html")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run.py server", description="Kamera paylasim server'i")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args(argv)

    print(f"Server calisiyor: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, threaded=True)


if __name__ == "__main__":
    main()
