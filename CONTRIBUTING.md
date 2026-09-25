# Trabajo en equipo

Flujo recomendado para dos integrantes:

1. `git pull` antes de empezar.
2. Crear una rama corta si ambas modificarán código al mismo tiempo: `git switch -c nombre-cambio`.
3. Hacer cambios pequeños y commits descriptivos.
4. Ejecutar `pytest -q` y el pipeline antes de subir.
5. No editar simultáneamente el mismo archivo si pueden evitarlo.
6. Nunca subir `.env` ni credenciales.

Roles sugeridos:

- **Scraping:** `scraper/` y adaptación de fuentes reales.
- **API:** `mock_api/` y `api_clients/`.
- **Integración/robustez:** `pipeline/`, logging, validaciones y dashboard técnico.
