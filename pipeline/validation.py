from __future__ import annotations

import pandas as pd

REQUIRED_PRODUCT_FIELDS = ["product_id", "product_name", "store", "price_mxn", "available"]


def validate_raw_products(products: list[dict]) -> dict:
    if not products:
        return {
            "records": 0,
            "missing_required": 0,
            "duplicate_store_product": 0,
            "invalid_price": 0,
            "quality_pct": 0.0,
        }

    df = pd.DataFrame(products)
    missing_required = 0
    for field in REQUIRED_PRODUCT_FIELDS:
        if field not in df.columns:
            missing_required += len(df)
        else:
            missing_required += int(df[field].isna().sum())
            if df[field].dtype == object:
                missing_required += int((df[field].astype(str).str.strip() == "").sum())

    duplicate_count = int(df.duplicated(subset=["store", "product_id"]).sum())
    price = pd.to_numeric(df.get("price_mxn"), errors="coerce")
    invalid_price = int((price.isna() | (price <= 0)).sum())

    bad = min(len(df), missing_required + duplicate_count + invalid_price)
    quality = round(max(0.0, (1 - bad / max(1, len(df))) * 100), 2)
    return {
        "records": int(len(df)),
        "missing_required": int(missing_required),
        "duplicate_store_product": duplicate_count,
        "invalid_price": invalid_price,
        "quality_pct": quality,
    }


def validate_integrated(catalog: pd.DataFrame) -> dict:
    if catalog.empty:
        return {"records": 0, "without_reviews": 0, "without_traits": 0}
    without_reviews = int((catalog["review_count"] <= 0).sum()) if "review_count" in catalog else len(catalog)
    without_traits = int(catalog["sunlight"].isna().sum()) if "sunlight" in catalog else len(catalog)
    return {
        "records": int(len(catalog)),
        "without_reviews": without_reviews,
        "without_traits": without_traits,
    }
