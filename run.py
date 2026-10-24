"""Tek giris noktasi: server veya client'i calistirir.

    python run.py server [--host 0.0.0.0] [--port 5000]
    python run.py client [--server 192.168.1.10:5000] [--camera 0] ...

Her modun kendi secenekleri icin: python run.py server -h / python run.py client -h
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
MODES = {
    "server": ROOT / "server",
    "client": ROOT / "client",
}
USAGE = "Kullanim: python run.py {server,client} [secenekler]\nDetay icin: python run.py server -h / python run.py client -h"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0 if len(sys.argv) >= 2 else 2)

    mode, argv = sys.argv[1], sys.argv[2:]
    if mode not in MODES:
        print(f"Bilinmeyen mod: {mode}\n{USAGE}")
        sys.exit(2)

    # Sadece secilen modun bagimliliklari yuklensin (server icin OpenCV gerekmez)
    sys.path.insert(0, str(MODES[mode]))
    if mode == "server":
        import app as module
    else:
        import client as module
    module.main(argv)


if __name__ == "__main__":
    main()
