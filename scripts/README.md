# scripts/ — pipeline de datos offline (dueño: P4, Fase 1)

Se ejecutan ANTES de la demo; la app nunca llama a APIs externas en tiempo de ejecución.

Pendiente (Fase 1):
- `build_grid.py`: grilla 0.25° sobre el bbox de Jujuy (≈ lat −21.75 a −24.6, lon −67.25 a −64.15), recortada con el límite provincial (fuente a citar).
- `fetch_nasa_power.py`: por celda, climatología `ALLSKY_SFC_SW_DWN` (kWh/m²/día) y `WS50M` (m/s); caché en `data/raw/`; respetar límites de uso.
- Salida: `data/processed/cells.geojson` según contrato C1 (`docs/CONTRACTS.md`), con `quality` por campo.
