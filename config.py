from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

PRACTICE_STORE_BASE_URL = os.getenv("PRACTICE_STORE_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
REVIEW_API_BASE_URL = os.getenv("REVIEW_API_BASE_URL", "http://127.0.0.1:8002").rstrip("/")
MOCK_API_KEY = os.getenv("MOCK_API_KEY", "plantmatch-demo-key")

REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BACKOFF_BASE_SECONDS = float(os.getenv("BACKOFF_BASE_SECONDS", "1"))

LANDING_DIR = ROOT / "landing"
PROCESSED_DIR = ROOT / "processed"
LOG_DIR = ROOT / "logs"
ERROR_DIR = ROOT / "errors"
REPORT_DIR = ROOT / "reports"

STORE_SOURCES = [
    {"store": "Vivero Norte", "url": f"{PRACTICE_STORE_BASE_URL}/store_norte.html"},
    {"store": "Casa Verde", "url": f"{PRACTICE_STORE_BASE_URL}/store_casa_verde.html"},
    {"store": "Patio Botánico", "url": f"{PRACTICE_STORE_BASE_URL}/store_patio.html"},
]
