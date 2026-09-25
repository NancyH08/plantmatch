from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


OPTIONAL_COLUMNS = {
    "family": "",
    "rareza": "",
    "product_url": "",
    "source_url": "",
    "size": "",
    "scientific_name": "",
    "common_name": "",
    "plant_type": "",
    "sunlight": "",
    "watering": "",
    "placement": "",
    "store": "",
    "avg_rating": 0.0,
    "review_count": 0,
    "available": False,
}


def prepare_catalog(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize UI-facing columns without changing the ingestion model."""
    if df.empty:
        return df.copy()

    result = df.copy()
    for column, default in OPTIONAL_COLUMNS.items():
        if column not in result.columns:
            result[column] = default

    if "available" in result.columns:
        mapped = result["available"].astype(str).str.lower().map({"true": True, "false": False})
        result["available"] = mapped.where(mapped.notna(), result["available"]).fillna(False).astype(bool)

    if "price_mxn" in result.columns:
        result["price_mxn"] = pd.to_numeric(result["price_mxn"], errors="coerce")
    result["avg_rating"] = pd.to_numeric(result["avg_rating"], errors="coerce").fillna(0.0)
    result["review_count"] = pd.to_numeric(result["review_count"], errors="coerce").fillna(0).astype(int)
    return result


def has_real_values(series: pd.Series) -> bool:
    if series.empty:
        return False
    cleaned = series.fillna("").astype(str).str.strip()
    return cleaned.ne("").any()


def rarity_column(df: pd.DataFrame) -> str | None:
    """Support the Spanish field requested by the project without inventing values."""
    for name in ("rareza", "rarity"):
        if name in df.columns and has_real_values(df[name]):
            return name
    return None


def is_rare(value: object) -> bool:
    text = str(value or "").strip().lower()
    return text in {"rara", "raro", "rare", "colección especial", "coleccion especial", "especial"}


def unique_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return sorted(values.unique().tolist(), key=str.casefold)


def filter_catalog(
    df: pd.DataFrame,
    *,
    query: str = "",
    families: Iterable[str] = (),
    sunlight: Iterable[str] = (),
    watering: Iterable[str] = (),
    placements: Iterable[str] = (),
    plant_types: Iterable[str] = (),
    stores: Iterable[str] = (),
    max_price: float | None = None,
    min_rating: float = 0.0,
    available_only: bool = False,
    rare_only: bool = False,
) -> pd.DataFrame:
    result = prepare_catalog(df)
    if result.empty:
        return result

    query = query.strip()
    if query:
        escaped = re.escape(query)
        common = result["common_name"].fillna("").astype(str)
        product = result.get("product_name", pd.Series("", index=result.index)).fillna("").astype(str)
        scientific = result["scientific_name"].fillna("").astype(str)
        mask = (
            common.str.contains(escaped, case=False, na=False, regex=True)
            | product.str.contains(escaped, case=False, na=False, regex=True)
            | scientific.str.contains(escaped, case=False, na=False, regex=True)
        )
        result = result[mask]

    selection_map = {
        "family": list(families),
        "sunlight": list(sunlight),
        "watering": list(watering),
        "placement": list(placements),
        "plant_type": list(plant_types),
        "store": list(stores),
    }
    for column, selected in selection_map.items():
        if selected:
            result = result[result[column].isin(selected)]

    if max_price is not None and "price_mxn" in result.columns:
        result = result[result["price_mxn"] <= max_price]
    result = result[result["avg_rating"] >= min_rating]

    if available_only:
        result = result[result["available"] == True]  # noqa: E712

    if rare_only:
        rare_col = rarity_column(result)
        if rare_col:
            result = result[result[rare_col].map(is_rare)]
        else:
            return result.iloc[0:0]

    return result
