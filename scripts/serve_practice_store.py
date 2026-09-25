from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "practice_store"
HOST = "127.0.0.1"
PORT = 8001

if __name__ == "__main__":
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer((HOST, PORT), handler)
    print(f"E-commerce de práctica: http://{HOST}:{PORT}")
    print("Ctrl+C para detener.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
