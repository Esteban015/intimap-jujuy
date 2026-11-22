# scripts/ — pipeline de datos offline

Estos scripts se ejecutan **antes** de la demo; la app nunca llama a APIs climáticas mientras corre. Dependencia: `pip install -r scripts/requirements.txt` (Shapely).

| Script | Qué hace | Salida |
|---|---|---|
| `build_grid.py [--offline]` | Descarga el contorno de Jujuy del IGN (respaldo: geoBoundaries, marcado como NO oficial), genera la grilla de 0,25° y la recorta. | `data/processed/jujuy.geojson`, `data/processed/grid.geojson` y la caché `data/raw/boundary_*.json` |
| `fetch_data.py [--offline] [--limit N]` | Por celda consulta NASA POWER (climatología `ALLSKY_SFC_SW_DWN`, `T2M`, `WS50M`) y, por lotes, Open-Meteo (altitud). Calcula los indicadores con `backend/app/indicators.py` y los normaliza. | `data/processed/cells.geojson` y la caché en `data/raw/nasa_power/` y `data/raw/open_meteo_elevation.json` |

Reglas del pipeline:
- Timeout de 60 s, 2 reintentos y pausa de 1 s entre consultas.
- Un fallo deja el campo en `null` con calidad `faltante`; nunca se rellena con datos sintéticos.
- Si no hay contorno disponible, el script falla: no se fabrica un límite.

Uso y regeneración: [`../docs/SETUP.md`](../docs/SETUP.md) §3. Metodología: [`../docs/DATA_METHODOLOGY.md`](../docs/DATA_METHODOLOGY.md).
