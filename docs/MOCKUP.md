# Mockup de arquitectura

```text
┌─────────────────────────────┐
│ E-commerce de plantas       │
│ tienda A / B / C            │
└─────────────┬───────────────┘
              │ HTTP + scraping
              ▼
┌─────────────────────────────┐
│ scraper/plant_store.py      │
│ nombre · precio · stock     │
└─────────────┬───────────────┘
              │
              │ productos.jsonl
              ▼
┌─────────────────────────────────────────────────┐
│ LANDING ZONE                                    │
│ landing/<fecha>/<run_id>/                       │
│  ├─ productos.jsonl                             │
│  ├─ resenas.jsonl                               │
│  └─ rasgos_botanicos.jsonl                      │
└────────────────▲────────────────▲───────────────┘
                 │                │
       resenas   │                │ rasgos
                 │                │
┌────────────────┴───┐       ┌────┴─────────────────┐
│ API REST /reviews  │       │ API REST /traits    │
│ X-API-Key          │       │ X-API-Key           │
│ paginación         │       │ paginación          │
└────────────────────┘       └──────────────────────┘
                 │                │
                 └───────┬────────┘
                         ▼
              ┌───────────────────────┐
              │ Integración/validación│
              │ product_id            │
              └──────────┬────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     processed/plants_catalog.csv   reports/*.json
              │                     logs/pipeline.log
              ▼                     errors/*.jsonl
     Streamlit: filtros / dashboard
```

## Formatos

- Scraping crudo: JSONL.
- Reseñas crudas: JSONL.
- Rasgos crudos: JSONL.
- Catálogo integrado: CSV.
- Reporte de validación: JSON.
- Log técnico: texto `.log`.

## Fallos y trazabilidad

Cada petición HTTP usa timeout, reintentos y backoff. Una fuente que falla se registra en `pipeline.log` y `errors/no_procesados.jsonl`; el orquestador continúa con el resto de fuentes.
