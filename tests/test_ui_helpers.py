import pandas as pd

from ui_helpers import filter_catalog, rarity_column


def sample_df():
    return pd.DataFrame([
        {
            "product_id": "monstera-deliciosa",
            "product_name": "Costilla de Adán",
            "common_name": "Monstera deliciosa",
            "scientific_name": "Monstera deliciosa",
            "family": "Araceae",
            "sunlight": "Luz indirecta",
            "watering": "Medio",
            "placement": "Interior",
            "plant_type": "Tropical",
            "store": "Casa Verde",
            "price_mxn": 289,
            "available": True,
            "avg_rating": 4.7,
            "review_count": 6,
        },
        {
            "product_id": "aloe-vera",
            "product_name": "Sábila",
            "common_name": "Aloe vera",
            "scientific_name": "Aloe vera",
            "family": "Asphodelaceae",
            "sunlight": "Mucho sol",
            "watering": "Bajo",
            "placement": "Interior/Exterior",
            "plant_type": "Suculenta",
            "store": "Vivero Norte",
            "price_mxn": 99,
            "available": True,
            "avg_rating": 4.8,
            "review_count": 6,
        },
    ])


def test_search_matches_common_or_scientific_name():
    df = sample_df()
    result = filter_catalog(df, query="monstera")
    assert result["product_id"].tolist() == ["monstera-deliciosa"]


def test_family_and_care_filters_work_together():
    df = sample_df()
    result = filter_catalog(
        df,
        families=["Asphodelaceae"],
        sunlight=["Mucho sol"],
        watering=["Bajo"],
        max_price=150,
    )
    assert result["product_id"].tolist() == ["aloe-vera"]


def test_rarity_filter_is_disabled_when_data_does_not_exist():
    df = sample_df()
    assert rarity_column(df) is None
    result = filter_catalog(df, rare_only=True)
    assert result.empty
