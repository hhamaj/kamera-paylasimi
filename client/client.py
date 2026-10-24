"""Kamera client'i: kameradan goruntu alip server'a WebSocket ile gonderir."""

import argparse
import json
import sys
import time

import cv2
import websocket


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="run.py client", description="Kamera paylasim client'i")
    parser.add_argument("--server", default="localhost:5000", help="Server adresi, ornek: 192.168.1.10:5000")
    parser.add_argument("--camera", type=int, default=0, help="Kamera numarasi (varsayilan 0)")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=float, default=15)
    parser.add_argument("--quality", type=int, default=70, help="JPEG kalitesi (1-100)")
    return parser.parse_args(argv)


def server_url(server):
    if server.startswith(("ws://", "wss://")):
        base = server
    else:
        base = "ws://" + server.removeprefix("http://")
    return base.rstrip("/") + "/ws/camera"


def open_camera(index, width, height):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        sys.exit(f"Kamera {index} acilamadi.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def stream(cap, ws, args):
    interval = 1.0 / args.fps
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, args.quality]
    while True:
        start = time.monotonic()
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Kameradan goruntu okunamadi.")
        if frame.shape[1] != args.width or frame.shape[0] != args.height:
            frame = cv2.resize(frame, (args.width, args.height))
        ok, jpeg = cv2.imencode(".jpg", frame, encode_params)
        if ok:
            ws.send(jpeg.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
        time.sleep(max(0.0, interval - (time.monotonic() - start)))


def main(argv=None):
    args = parse_args(argv)
    name = ""
    while not name:
        name = input("Kamera adi: ").strip()

    url = server_url(args.server)
    cap = open_camera(args.camera, args.width, args.height)

    try:
        while True:
            try:
                print(f"Baglaniliyor: {url}")
                ws = websocket.create_connection(url, timeout=10)
                ws.send(json.dumps({"name": name}))
                print("Baglandi, goruntu gonderiliyor. Cikmak icin Ctrl+C.")
                try:
                    stream(cap, ws, args)
                finally:
                    ws.close()
            except (OSError, websocket.WebSocketException) as e:
                print(f"Baglanti hatasi: {e}. 3 saniye sonra tekrar denenecek.")
                time.sleep(3)
    except KeyboardInterrupt:
        print("\nKapatiliyor.")
    except RuntimeError as e:
        print(e)
    finally:
        cap.release()


if __name__ == "__main__":
    main()
