from __future__ import annotations

import math
import os
from fastapi import FastAPI, Header, HTTPException, Query
from mock_api.data import PLANTS, REVIEWS

app = FastAPI(
    title="PlantMatch Practice API",
    description="API simulada para el proyecto de ingesta híbrida: reseñas, calificaciones y rasgos botánicos.",
    version="1.0.0",
)

API_KEY = os.getenv("MOCK_API_KEY", "plantmatch-demo-key")


def check_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")


@app.get("/health")
def health():
    return {"status": "ok", "service": "plantmatch-practice-api"}


@app.get("/reviews")
def reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    product_id: str | None = None,
    x_api_key: str | None = Header(default=None),
):
    check_key(x_api_key)
    rows = REVIEWS if product_id is None else [r for r in REVIEWS if r["product_id"] == product_id]
    total = len(rows)
    pages = max(1, math.ceil(total / per_page))
    start = (page - 1) * per_page
    items = rows[start:start + per_page]
    return {"page": page, "per_page": per_page, "total": total, "pages": pages, "items": items}


@app.get("/traits")
def traits(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    product_id: str | None = None,
    x_api_key: str | None = Header(default=None),
):
    check_key(x_api_key)
    rows = [{"product_id": key, **value} for key, value in PLANTS.items()]
    if product_id is not None:
        rows = [r for r in rows if r["product_id"] == product_id]
    total = len(rows)
    pages = max(1, math.ceil(total / per_page))
    start = (page - 1) * per_page
    items = rows[start:start + per_page]
    return {"page": page, "per_page": per_page, "total": total, "pages": pages, "items": items}
