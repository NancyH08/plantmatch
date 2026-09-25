from pipeline.integration import build_catalog


def test_build_catalog_merges_sources():
    products = [{
        "product_id": "aloe-vera", "product_name": "Sábila", "store": "Demo", "price_mxn": 99,
        "available": True, "size": "6", "product_url": "x", "source_url": "x", "ingested_at": "x"
    }]
    reviews = [
        {"review_id": "1", "product_id": "aloe-vera", "rating": 5, "comment": "ok", "created_at": "x"},
        {"review_id": "2", "product_id": "aloe-vera", "rating": 4, "comment": "ok", "created_at": "x"},
    ]
    traits = [{
        "product_id": "aloe-vera", "common_name": "Aloe vera", "scientific_name": "Aloe vera",
        "family": "Asphodelaceae", "sunlight": "Mucho sol", "watering": "Bajo", "placement": "Interior/Exterior", "plant_type": "Suculenta"
    }]
    df = build_catalog(products, reviews, traits)
    assert len(df) == 1
    assert df.iloc[0]["avg_rating"] == 4.5
    assert df.iloc[0]["sunlight"] == "Mucho sol"
    assert df.iloc[0]["family"] == "Asphodelaceae"
