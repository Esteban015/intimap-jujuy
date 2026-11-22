# Contratos de datos — IntiMap Jujuy (v0, Fase 0)

> Fuente de verdad de la integración. Cambiar un contrato = avisar al equipo y actualizar
> `backend/app/contracts.py` + este archivo en el mismo cambio (dueño: P1).

## Calidad de dato (obligatorio en todo valor mostrado) — v1 (Fase 1)
| Valor | Significado |
|---|---|
| `real` | Valor descargado de una fuente citada (NASA POWER, Open-Meteo) sin transformación más allá de la que hace el proveedor. |
| `estimado` | Derivado por fórmula a partir de valores `real` (p. ej. kWh/kWp, densidad del aire, índices 0-100). |
| `faltante` | La fuente falló o no devolvió dato: el valor es `null`. **Nunca** se rellena. |
| `sintetico` | Inventado para desarrollo. Solo en `data/sample/`. **Nunca** se presenta como medición. |

En la Fase 0 se usaba `aproximado`; ahora se reemplaza por `estimado` (vocabulario del enunciado de la Fase 1). El frontend debe tratar cualquier valor distinto de `real` como "no medido".

## C1. Celdas (datos estáticos) — `data/processed/cells.geojson` (v1)
- **Productor:** `scripts/build_grid.py` y luego `scripts/fetch_data.py`.
- **Consumidores:** el backend (`data_loader.py`) y el frontend a través de `/api/cells`.
- **Respaldo:** si el archivo no existe, o con `INTIMAP_DATASET=sample`, el backend usa `data/sample/cells.sample.geojson`, que es **sintético** (`metadata.synthetic=true` y `properties.synthetic=true`).

```jsonc
{
  "type": "FeatureCollection",
  "metadata": {
    "dataset": "processed | sample",       // lo que se entregó, sin ambigüedad
    "synthetic": false,
    "generated_at": "ISO-8601",
    "grid_resolution_deg": 0.25,
    "boundary_source": {"id": "ign_wfs", "official": true, "url": "...", "license": "...", "fetched_at": "..."},
    "climate_period": ["... (January 2001 - December 2025)"],
    "sources": [{"id": "nasa_power", ...}, {"id": "open_meteo_elevation", ...}],
    "variables": {"<campo>": {"unit": "...", "source|derived": "...", "desc": "..."}},
    "counts": {"cells": 104, "complete": 104, "with_missing": 0},
    "disclaimer": "..."
  },
  "features": [{
    "type": "Feature",
    "geometry": {"type": "Polygon | MultiPolygon"},  // celda YA recortada al contorno de Jujuy
    "properties": {
      "id": "c_-23.125_-65.375",          // estable: centro de la celda completa de 0,25°
      "centroid": [-23.125, -65.375],     // [lat, lon] centro de la celda completa
      "query_point": [-23.12, -65.37],    // [lat, lon] punto DENTRO de Jujuy usado para consultar las APIs
      "area_km2": 712.3,                  // área aproximada de la parte dentro de Jujuy
      "coverage_fraction": 1.0,           // fracción de la celda completa que cae dentro de Jujuy
      "solar_ghi_kwh_m2_day": 6.54,       // real · NASA POWER ALLSKY_SFC_SW_DWN, media anual
      "temp_mean_c": 7.66,                // real · NASA POWER T2M
      "wind_speed_50m_ms": 4.72,          // real · NASA POWER WS50M
      "wind_height_m": 50,
      "elevation_m": 3443,                // real · Open-Meteo (Copernicus DEM 90 m) en query_point
      "solar_kwh_kwp_year": 1780,         // estimado · fórmula spec §8
      "air_density_kg_m3": 0.86,          // estimado
      "wind_power_density_w_m2": 45.2,    // estimado · índice con v media, NO energía de turbina
      "s_solar": 0-100, "s_wind": 0-100,  // estimado · min-max entre celdas con dato
      "synthetic": false,
      "quality": {"<campo>": "real | estimado | faltante | sintetico"},
      "provenance": {"nasa_power": {"fetched_at": "...", "period": "..."}, "open_meteo_elevation": {"fetched_at": "..."}}
    }
  }]
}
```
Las unidades son fijas (ver `metadata.variables`). Un campo faltante es `null`, nunca un 0 inventado.
Las 6 celdas de la muestra solo traen el subconjunto de la Fase 0, así que el frontend debe tolerar campos ausentes.

## C1b. Contorno — `data/processed/jujuy.geojson` → `GET /api/boundary`
Es el contorno del IGN, simplificado a unos 200 m para dibujarlo. `metadata.source` indica la fuente, la licencia y la fecha de descarga.

## C2. API (FastAPI, prefijo `/api`)
| Método | Ruta | Fase | Estado |
|---|---|---|---|
| GET | `/api/health` | 0 | Implementado (dataset, synthetic, counts, climate_period) |
| GET | `/api/cells` | 0-1 | Implementado (C1 tal cual + header `X-IntiMap-Dataset`) |
| GET | `/api/boundary` | 1 | Implementado (C1b; 404 si no se generó) |
| GET | `/api/cells/{id}` | 0 | Implementado (404 si no existe) |
| POST | `/api/scores` | 2 | Implementado con `scoring.py` (verificación; la UI recalcula en el cliente) |
| POST | `/api/simulate` | 3 | Implementado con `finance.py` (solo solar, USD) |
| GET | `/api/scenario` | 3 | Implementado: escenario HIPOTÉTICO editable (`data/economic_scenario.json`) |
| POST | `/api/assistant` | 3 | Implementado: determinista + LLM opcional. Reemplaza a `/api/explain`, que fue retirado |

### POST `/api/scores`
Request: `{"weights": {"solar": 0-1, "wind": 0-1}}` (al menos uno > 0; se normalizan a suma 1).
Response:
```json
{
  "weights_normalized": {"solar": 0.7, "wind": 0.3},
  "method": "min-max relativo a las celdas de Jujuy",
  "cells": [{"id": "c_...", "solar_index": 0-100, "wind_index": 0-100, "score": 0-100}],
  "disclaimer": "Índice relativo entre zonas de Jujuy; no indica viabilidad absoluta."
}
```
Regla: índice = 100·(x − min)/(max − min) sobre celdas con dato; celda sin dato → índice `null` y `score` calculado solo con los componentes disponibles (re-normalizando pesos), marcando `partial: true`.


### POST `/api/simulate` (solo solar, USD) — v1 (Fase 3)
Request (pydantic `SimulateRequest`). `null` u omitido significa "no informado":
```json
{"cell_id": "c_...", "system_kwp": 5, "cost_per_kwp_usd": 900, "energy_value_usd_kwh": 0.10,
 "self_consumption_pct": 80, "om_usd_year": null, "export_value_usd_kwh": null}
```
Validación (422 si falla):
- `system_kwp` en (0, 10000].
- Costos y tarifas mayores o iguales a 0.
- `self_consumption_pct` en [0, 100].

Si la celda no existe, la respuesta es 404.

Response: `{cell_id, solar_kwh_kwp_year, synthetic, inputs, currency: "USD", results: {annual_kwh, self_consumed_kwh, surplus_kwh, capex_usd, export_value_usd_year, gross_savings_usd_year, om_usd_year, net_savings_usd_year, simple_payback_years}, not_calculable: {campo: motivo}, warnings[], limitations[], formulas{}, disclaimer}`.

Reglas de cálculo:
- Un resultado que no se puede calcular vale `null` y su motivo va en `not_calculable`. La UI muestra «No calculable».
- El excedente no tiene valor salvo que se informe `export_value_usd_kwh`.
- Si el mantenimiento no se declara, se toma 0 y se agrega una advertencia.
- No hay recuperación si el ahorro neto es menor o igual a 0.
- **No existe simulación eólica en kWh.**

### GET `/api/scenario`
Devuelve los valores por defecto del simulador, rotulados "ESCENARIO HIPOTÉTICO EDITABLE". Vienen de los ejemplos del spec §8, no son cotizaciones.

### POST `/api/assistant` — v1 (Fase 3)
Request: `{"question": "1-500 caracteres", "selected_cell_id": "c_... | null", "weights": {"solar": 0-1, "wind": 0-1}, "scenario": <SimulateRequest sin cell_id> | null}`.
Errores: 422 si la pregunta está vacía o ambos pesos valen 0; 404 si la celda no existe.

Response:
```json
{"answer": "1) Recomendación: …\n2) Por qué: …\n3) Advertencia: …",
 "mode": "deterministic | llm", "llm_fallback_reason": "… | null", "intent": "explain|where|wind|economics|community",
 "sections": {"recommendation", "justification", "warning"} | null, "cell_ids": [...], "facts_used": {...}, "words": 97}
```

Reglas:
- La respuesta tiene como máximo 150 palabras y siempre las tres secciones.
- El contexto se arma solo con el dataset cargado, el ranking con los pesos actuales, la celda elegida y el escenario.
- El LLM (opcional) solo reescribe el borrador determinista. Se descarta si cambia números, se excede de palabras, pierde secciones, falla, tarda o se niega.
- La clave `LLM_API_KEY` solo existe en el backend.

## C3. Supuestos económicos
- **Vigente:** `data/economic_scenario.json`, en USD y con etiqueta de escenario hipotético.
- **Obsoleto:** `data/assumptions.json` (de P3), que usa ARS y PR 0,75. No se tocó; P3 debe retirarlo o alinearlo (ver DECISIONS 31).
