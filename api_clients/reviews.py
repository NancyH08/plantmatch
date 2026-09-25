from __future__ import annotations

from config import MOCK_API_KEY, REVIEW_API_BASE_URL
from utils.network import request_with_retry


def fetch_reviews(logger, product_ids: set[str] | None = None) -> list[dict]:
    page = 1
    rows: list[dict] = []
    headers = {"X-API-Key": MOCK_API_KEY}

    while True:
        response = request_with_retry(
            "GET",
            f"{REVIEW_API_BASE_URL}/reviews",
            logger=logger,
            headers=headers,
            params={"page": page, "per_page": 10},
        )
        payload = response.json()
        rows.extend(payload["items"])
        if page >= payload["pages"]:
            break
        page += 1

    if product_ids is not None:
        rows = [r for r in rows if r.get("product_id") in product_ids]
    logger.info("API reseñas: %s registros", len(rows))
    return rows
