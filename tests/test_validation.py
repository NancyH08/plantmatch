from pipeline.validation import validate_raw_products


def test_validation_detects_clean_rows():
    rows = [
        {"product_id": "a", "product_name": "A", "store": "S1", "price_mxn": 100, "available": True},
        {"product_id": "a", "product_name": "A", "store": "S2", "price_mxn": 110, "available": False},
    ]
    result = validate_raw_products(rows)
    assert result["records"] == 2
    assert result["duplicate_store_product"] == 0
    assert result["invalid_price"] == 0
    assert result["quality_pct"] == 100.0


def test_validation_detects_duplicate_and_bad_price():
    rows = [
        {"product_id": "a", "product_name": "A", "store": "S1", "price_mxn": 0, "available": True},
        {"product_id": "a", "product_name": "A", "store": "S1", "price_mxn": 100, "available": True},
    ]
    result = validate_raw_products(rows)
    assert result["duplicate_store_product"] == 1
    assert result["invalid_price"] == 1
