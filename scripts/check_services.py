from __future__ import annotations

import sys
import requests
from config import MOCK_API_KEY, PRACTICE_STORE_BASE_URL, REVIEW_API_BASE_URL

checks = [
    ("E-commerce de práctica", PRACTICE_STORE_BASE_URL, {}),
    ("API health", f"{REVIEW_API_BASE_URL}/health", {}),
    ("API reseñas autenticada", f"{REVIEW_API_BASE_URL}/reviews?page=1&per_page=1", {"X-API-Key": MOCK_API_KEY}),
]

ok = True
for name, url, headers in checks:
    try:
        r = requests.get(url, headers=headers, timeout=3)
        r.raise_for_status()
        print(f"[OK] {name}: {url}")
    except Exception as exc:
        ok = False
        print(f"[ERROR] {name}: {exc}")

if not ok:
    print("\nRevisa que estén ejecutándose el servidor de práctica y uvicorn.")
    sys.exit(1)

print("\nTodo listo. Ejecuta: python -m pipeline.orchestrator")
