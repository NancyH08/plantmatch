from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils.network import request_with_retry


def scrape_store(source: dict, logger) -> list[dict]:
    response = request_with_retry("GET", source["url"], logger=logger)
    soup = BeautifulSoup(response.text, "html.parser")
    rows: list[dict] = []

    for card in soup.select(".product-card"):
        price_node = card.select_one(".price")
        availability_node = card.select_one(".availability")
        link_node = card.select_one(".product-link")
        name_node = card.select_one(".product-name")
        size_node = card.select_one(".size")

        if not (price_node and availability_node and name_node):
            continue

        rows.append({
            "product_id": card.get("data-product-id", "").strip(),
            "scientific_name": card.get("data-scientific-name", "").strip(),
            "product_name": name_node.get_text(" ", strip=True),
            "store": source["store"],
            "price_mxn": float(price_node.get("data-price", "0")),
            "available": availability_node.get("data-available", "false").lower() == "true",
            "size": size_node.get_text(" ", strip=True) if size_node else None,
            "product_url": urljoin(source["url"], link_node.get("href", "")) if link_node else source["url"],
            "source_url": source["url"],
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        })

    logger.info("Scraping %s: %s productos", source["store"], len(rows))
    return rows
