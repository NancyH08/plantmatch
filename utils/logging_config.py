from __future__ import annotations

import logging
from config import LOG_DIR
from utils.io_utils import ensure_dir


def configure_logging() -> logging.Logger:
    ensure_dir(LOG_DIR)
    logger = logging.getLogger("plantmatch")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
