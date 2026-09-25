# PlantMatch

Pipeline de ingesta híbrida para **Ingeniería de Datos 2026**. Integra:

1. **Web Scraping** de un e-commerce de práctica con tres tiendas de plantas.
2. **API REST simulada** de reseñas/calificaciones con autenticación y paginación.
3. **API REST simulada de rasgos botánicos** para habilitar filtros por luz, riego y ubicación.
4. **Landing Zone**, logging, reintentos con backoff, archivo de no procesados y reporte de validación.
5. **Streamlit** como interfaz web local para explorar, comparar y revisar el estado del pipeline.

> El modo demo es deliberadamente reproducible: funciona en las dos computadoras sin depender de que un sitio real cambie su HTML o bloquee el scraping. La arquitectura permite reemplazar después las URLs/parseadores por viveros reales.

## Requisitos

- Python **3.11** recomendado.
- Git.
- Windows, macOS o Linux.

## 1. Clonar y crear el entorno

### Windows PowerShell

```powershell
git clone URL_DEL_REPOSITORIO
cd plantmatch
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS / Linux

```bash
git clone URL_DEL_REPOSITORIO
cd plantmatch
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Levantar las fuentes de práctica

Abre una terminal con el entorno activo:

```bash
python -m scripts.serve_practice_store
```

El e-commerce queda en `http://127.0.0.1:8001`.

Abre una segunda terminal, activa el mismo entorno y ejecuta:

```bash
uvicorn mock_api.main:app --host 127.0.0.1 --port 8002
```

La API queda en `http://127.0.0.1:8002`. Su documentación interactiva está en `http://127.0.0.1:8002/docs`.

Comprueba ambas fuentes con:

```bash
python -m scripts.check_services
```

## 3. Ejecutar el pipeline

En una tercera terminal con el entorno activo:

```bash
python -m pipeline.orchestrator
```

El pipeline genera:

```text
landing/<fecha>/<run_id>/productos.jsonl
landing/<fecha>/<run_id>/resenas.jsonl
landing/<fecha>/<run_id>/rasgos_botanicos.jsonl
processed/plants_catalog.csv
processed/latest_run.json
reports/validation_<run_id>.json
logs/pipeline.log
errors/no_procesados.jsonl
```

## 4. Ejecutar la prueba de tolerancia a fallos

```bash
python -m pipeline.orchestrator --simulate-failure
```

Se agrega una fuente deliberadamente inválida. El error queda registrado, pero el pipeline continúa con las fuentes disponibles.

## 5. Abrir la web

```bash
streamlit run app.py
```

En la computadora: `http://localhost:8501`

Como `.streamlit/config.toml` escucha en `0.0.0.0`, también puede abrirse desde un celular conectado a la **misma red Wi‑Fi** usando:

```text
http://IP_DE_LA_COMPUTADORA:8501
```

En Windows puedes consultar la IP con `ipconfig`; en macOS/Linux, con `ip addr` o `ifconfig`. Si no abre desde el celular, revisa el firewall y permite conexiones privadas al puerto 8501.

## Flujo del proyecto

```text
[E-commerce de práctica] -- scraping --> [Scraper] -----------                                                              > [Landing cruda]
[API de reseñas] -------- API REST --> [Cliente reseñas] -----/
[API botánica] ---------- API REST --> [Cliente rasgos] ------/
                                                |
                                                v
                                      [Validación / integración]
                                                |
                             +------------------+------------------+
                             |                                     |
                    [Catálogo procesado]                  [Logs / errores]
                             |
                             v
                    [Streamlit: filtros]
```

## Identificador común

El modo demo utiliza `product_id` como identificador estable. Ejemplos:

- `aloe-vera`
- `monstera-deliciosa`
- `dracaena-trifasciata`

En fuentes reales, este identificador se obtendría mediante SKU cuando exista o mediante normalización/matching del nombre comercial y nombre científico.

## Filtros de la interfaz

La vista **Explorar plantas** permite:

- buscar por nombre común, nombre publicado o nombre científico;
- filtrar por familia botánica;
- filtrar por luz, frecuencia de riego, interior/exterior y tipo de planta;
- conservar los filtros de precio máximo, calificación mínima, disponibilidad y tienda;
- consultar todas las ofertas encontradas por scraping, con precio, disponibilidad y enlace del producto.

El catálogo incluye `family` desde la API botánica simulada. La interfaz también está preparada para un campo opcional `rareza` (o `rarity`): el filtro y la insignia solo aparecen cuando los datos realmente contienen ese valor; la UI no clasifica plantas como raras por su cuenta.

La vista **Comparar** muestra hasta tres especies en formato lado a lado y conserva sus opciones de compra. La vista **Pipeline** permanece separada y muestra conteos, estado, duración, calidad de datos, errores, fuentes procesadas y las últimas líneas del log.

## Pruebas automáticas

```bash
pytest -q
```

## Trabajo en GitHub entre dos personas

Antes de comenzar:

```bash
git pull
```

Al terminar:

```bash
git add .
git commit -m "Describe brevemente el cambio"
git push
```

No suban `.env`, `.venv` ni archivos de logs. El `.gitignore` ya los excluye.

## Documentación del parcial

- `docs/PROYECTO.md`: propuesta limpia y relación con la rúbrica.
- `docs/MOCKUP.md`: arquitectura y formatos.
- `docs/DEFENSA.md`: guion breve para la defensa.
- `docs/PRUEBAS.md`: resultados de pruebas técnicas verificadas.
