from __future__ import annotations

import pandas as pd


def build_catalog(products: list[dict], reviews: list[dict], traits: list[dict]) -> pd.DataFrame:
    product_df = pd.DataFrame(products)
    if product_df.empty:
        return product_df

    review_df = pd.DataFrame(reviews)
    if review_df.empty:
        review_summary = pd.DataFrame(columns=["product_id", "avg_rating", "review_count"])
    else:
        review_summary = (
            review_df.groupby("product_id", as_index=False)
            .agg(avg_rating=("rating", "mean"), review_count=("review_id", "count"))
        )
        review_summary["avg_rating"] = review_summary["avg_rating"].round(2)

    trait_df = pd.DataFrame(traits)
    merged = product_df.merge(review_summary, on="product_id", how="left")
    if not trait_df.empty:
        trait_cols = [
            "product_id", "common_name", "scientific_name", "sunlight",
            "watering", "placement", "plant_type"
        ]
        trait_df = trait_df[[c for c in trait_cols if c in trait_df.columns]]
        merged = merged.drop(columns=["scientific_name"], errors="ignore").merge(trait_df, on="product_id", how="left")

    merged["avg_rating"] = merged.get("avg_rating", 0).fillna(0)
    merged["review_count"] = merged.get("review_count", 0).fillna(0).astype(int)
    merged["price_mxn"] = pd.to_numeric(merged["price_mxn"], errors="coerce")
    return merged.sort_values(["product_id", "price_mxn", "store"]).reset_index(drop=True)
