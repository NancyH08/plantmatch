# Propuesta limpia — PlantMatch

## Título

**PlantMatch: sistema de filtrado y comparación de plantas mediante una arquitectura de ingesta híbrida**

## Problema

Las tiendas en línea muestran precio y disponibilidad, pero la información de cuidado suele ser inconsistente o difícil de comparar. PlantMatch integra datos comerciales con reseñas y características botánicas para permitir filtros útiles como luz, riego, interior/exterior, precio, calificación, disponibilidad y tienda.

## Fuente 1 — Web Scraping

Se extraen de un e-commerce real o de práctica:

- nombre del producto;
- precio;
- disponibilidad;
- tienda;
- presentación;
- URL;
- identificador del producto.

## Fuente 2 — API de reseñas

Se consume una API REST simulada, permitida por la rúbrica, con:

- autenticación por `X-API-Key`;
- paginación;
- reseña individual;
- calificación;
- fecha;
- `product_id`.

## Fuente complementaria — rasgos botánicos

El mismo servicio de práctica expone un endpoint adicional con:

- luz;
- riego;
- interior/exterior;
- tipo de planta;
- nombre científico.

Este endpoint es una ampliación funcional; el requisito base ya queda cubierto por scraping + API de reseñas.

## Identificador común

`product_id`. En un escenario con tiendas reales se reemplaza por SKU cuando exista o por un identificador normalizado derivado del nombre comercial/nombre científico.

## Resultado

El Parcial 1 produce la ingesta y los archivos crudos. Streamlit actúa como demostrador y permite filtrar el catálogo integrado sin convertir el proyecto en una app móvil dedicada.

## Correspondencia con la rúbrica

| Requisito | Implementación |
|---|---|
| Web Scraping | `scraper/plant_store.py` |
| API de reseñas | `/reviews` + `api_clients/reviews.py` |
| Autenticación | `X-API-Key` |
| Paginación | `page` / `per_page` |
| Landing | `landing/<fecha>/<run_id>/` |
| Identificador común | `product_id` |
| Manejo de errores | `try/except` por fuente |
| Reintentos | `utils/network.py` con backoff exponencial |
| Logging | `logs/pipeline.log` |
| No procesados | `errors/no_procesados.jsonl` |
| Calidad de datos | `pipeline/validation.py` |
| Prueba de tolerancia | `--simulate-failure` |
| Reporte de validación | `reports/validation_<run_id>.json` |
