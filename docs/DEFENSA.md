# Guion breve de defensa

## 1. Qué hace

PlantMatch es un pipeline híbrido que extrae productos de tiendas de plantas mediante scraping y consume una API de reseñas. Conserva las fuentes crudas en una Landing Zone y genera un catálogo integrado para demostrar filtros en Streamlit.

## 2. Por qué hay tres archivos crudos

`productos.jsonl` contiene la fuente web; `resenas.jsonl` contiene la fuente API obligatoria; `rasgos_botanicos.jsonl` es una ampliación que permite los filtros de luz, riego e interior/exterior.

## 3. Cómo se relacionan

Todas las fuentes usan `product_id`. En un sitio real, el matching se haría por SKU o mediante normalización del nombre y nombre científico.

## 4. Robustez

Las peticiones tienen timeout y reintentos con backoff exponencial. Un fallo se escribe en `logs/pipeline.log` y `errors/no_procesados.jsonl`. El pipeline no se detiene por una sola fuente.

## 5. Prueba de fallo

Ejecutar:

```bash
python -m pipeline.orchestrator --simulate-failure
```

Se añade una URL inválida. Debe aparecer un error en el log y aun así generarse el resto de archivos.

## 6. Calidad

`pipeline/validation.py` revisa campos requeridos, precios inválidos y duplicados por tienda/producto. Se genera un JSON de validación por ejecución.

## 7. Demostración

1. Mostrar `landing/` y explicar que son datos crudos.
2. Mostrar `logs/pipeline.log`.
3. Abrir Streamlit.
4. Filtrar “Mucho sol”, “Riego bajo”, precio máximo y disponibilidad.
5. Abrir “Pipeline” y mostrar los conteos de la última ejecución.
