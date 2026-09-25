# Evidencia de pruebas realizadas durante la preparación

## Tests unitarios

```text
3 passed
```

Cubren validación de datos y unión de scraping + reseñas + rasgos botánicos.

## Ejecución completa

Resultado verificado:

```text
status: ok
products: 25
reviews: 63
traits: 12
errors: 0
quality_pct: 100.0
```

El catálogo integrado resultante contiene 25 ofertas comerciales, 12 especies y 3 tiendas. Ningún registro quedó sin rasgos botánicos ni reseñas.

## Tolerancia a fallos

Se ejecutó:

```bash
python -m pipeline.orchestrator --simulate-failure
```

Resultado verificado:

```text
status: partial
products: 25
reviews: 63
traits: 12
errors: 1
quality_pct: 100.0
```

La fuente simulada falló tres veces. El módulo aplicó backoff, registró el error y continuó con las demás fuentes.

## Verificación estática

Todo el código Python se compiló con `python -m compileall` sin errores de sintaxis.

La interfaz Streamlit queda incluida y configurada; debe validarse visualmente en la computadora del equipo después de instalar las dependencias de `requirements.txt`.
