from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

from api_clients.reviews import fetch_reviews
from api_clients.traits import fetch_traits
from config import ERROR_DIR, LANDING_DIR, PROCESSED_DIR, REPORT_DIR, STORE_SOURCES
from pipeline.integration import build_catalog
from pipeline.validation import validate_integrated, validate_raw_products
from scraper.plant_store import scrape_store
from utils.io_utils import append_jsonl, ensure_dir, write_json, write_jsonl
from utils.logging_config import configure_logging


def ejecutar_pipeline(simulate_failure: bool = False) -> dict:
    logger = configure_logging()
    started = datetime.now(timezone.utc)
    start_perf = time.perf_counter()
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ensure_dir(LANDING_DIR / started.strftime("%Y-%m-%d") / run_id)
    errors: list[dict] = []

    logger.info("=== Iniciando pipeline %s ===", run_id)

    sources = list(STORE_SOURCES)
    if simulate_failure:
        sources.append({"store": "Fuente caída simulada", "url": "http://127.0.0.1:65530/no-existe"})

    products: list[dict] = []
    for source in sources:
        try:
            products.extend(scrape_store(source, logger))
        except Exception as exc:
            error = {
                "run_id": run_id,
                "stage": "scraping",
                "source": source["store"],
                "url": source["url"],
                "error": str(exc),
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            }
            errors.append(error)
            append_jsonl(ERROR_DIR / "no_procesados.jsonl", error)
            logger.error("Error en scraping de %s: %s", source["store"], exc)

    write_jsonl(run_dir / "productos.jsonl", products)
    product_ids = {p["product_id"] for p in products if p.get("product_id")}

    reviews: list[dict] = []
    try:
        reviews = fetch_reviews(logger, product_ids)
    except Exception as exc:
        error = {
            "run_id": run_id,
            "stage": "api_reviews",
            "source": "reviews_api",
            "error": str(exc),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        errors.append(error)
        append_jsonl(ERROR_DIR / "no_procesados.jsonl", error)
        logger.error("Error en API de reseñas: %s", exc)
    write_jsonl(run_dir / "resenas.jsonl", reviews)

    traits: list[dict] = []
    try:
        traits = fetch_traits(logger, product_ids)
    except Exception as exc:
        error = {
            "run_id": run_id,
            "stage": "api_traits",
            "source": "traits_api",
            "error": str(exc),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        errors.append(error)
        append_jsonl(ERROR_DIR / "no_procesados.jsonl", error)
        logger.error("Error en API botánica: %s", exc)
    write_jsonl(run_dir / "rasgos_botanicos.jsonl", traits)

    raw_validation = validate_raw_products(products)
    catalog = build_catalog(products, reviews, traits)
    integrated_validation = validate_integrated(catalog)

    ensure_dir(PROCESSED_DIR)
    catalog.to_csv(PROCESSED_DIR / "plants_catalog.csv", index=False)

    validation_report = {
        "run_id": run_id,
        "raw_products": raw_validation,
        "integrated_catalog": integrated_validation,
        "errors": len(errors),
    }
    write_json(REPORT_DIR / f"validation_{run_id}.json", validation_report)

    finished = datetime.now(timezone.utc)
    duration = round(time.perf_counter() - start_perf, 3)
    status = "failed" if not products else ("partial" if errors else "ok")
    store_counts: dict[str, int] = {}
    for p in products:
        store_counts[p["store"]] = store_counts.get(p["store"], 0) + 1

    latest_run = {
        "run_id": run_id,
        "status": status,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": duration,
        "products": len(products),
        "reviews": len(reviews),
        "traits": len(traits),
        "errors": len(errors),
        "store_counts": store_counts,
        "quality_pct": raw_validation["quality_pct"],
        "landing_path": str(run_dir),
    }
    write_json(PROCESSED_DIR / "latest_run.json", latest_run)

    logger.info(
        "Pipeline %s finalizado | estado=%s | productos=%s | reseñas=%s | rasgos=%s | errores=%s | %.3fs",
        run_id, status, len(products), len(reviews), len(traits), len(errors), duration,
    )
    return latest_run


def main():
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline híbrido PlantMatch")
    parser.add_argument("--simulate-failure", action="store_true", help="Agrega una fuente caída para probar tolerancia a fallos")
    args = parser.parse_args()
    result = ejecutar_pipeline(simulate_failure=args.simulate_failure)
    print("\nResumen:")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
