# Instalación y ejecución — IntiMap Jujuy

## Requisitos
- Python 3.11 o superior (probado con 3.13). Las versiones actuales de FastAPI y Shapely lo requieren.
- Git.
- Internet **solo** para instalar dependencias y, opcionalmente, para regenerar datos. La app funciona sin conexión.

## 1. Ejecutar la app (el dataset ya viene en el repositorio)

```bash
git clone https://github.com/Esteban015/intimap-jujuy.git
cd intimap-jujuy
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1   ·   Windows (Git Bash): source .venv/Scripts/activate
# Linux/Mac:            source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --port 8000
```

- App: http://localhost:8000
- API interactiva (Swagger): http://localhost:8000/docs
- Estado: http://localhost:8000/api/health. Tiene que mostrar `"dataset":"processed"` y `"cells":104`.

`--reload` es opcional, útil para desarrollar.

`backend/requirements.txt` fija las versiones validadas: FastAPI, Uvicorn, Pydantic, Starlette y el SDK `anthropic`. El SDK solo se usa si se define `LLM_API_KEY`; sin la clave, el asistente funciona en modo determinista.

## 2. Variables de entorno (opcionales)
Copiá `.env.example` como referencia. **La app no lee archivos `.env`**: definí las variables en la terminal antes de iniciar uvicorn.

| Variable | Valores | Efecto |
|---|---|---|
| `INTIMAP_DATASET` | `auto` (por defecto), `processed` o `sample` | `sample` carga 6 celdas **sintéticas** y la UI muestra un cartel rojo. |
| `LLM_API_KEY` | Clave de la API de Claude | Activa la redacción con IA del asistente, que valida la salida. |
| `LLM_MODEL` | Por defecto `claude-opus-5-5` | Modelo del LLM opcional. |

Ejemplos:
```bash
# Git Bash / Linux / Mac
INTIMAP_DATASET=sample python -m uvicorn backend.app.main:app --port 8000
# PowerShell
$env:INTIMAP_DATASET = "sample"; python -m uvicorn backend.app.main:app --port 8000
```

## 3. Regenerar el dataset (opcional)
Requiere Shapely:
```bash
pip install -r scripts/requirements.txt
```

**Sin red**, reconstruye desde la caché versionada en `data/raw/`:
```bash
python scripts/build_grid.py --offline
python scripts/fetch_data.py --offline
```

**Con red**, descarga solo lo que falte en la caché:
```bash
python scripts/build_grid.py
python scripts/fetch_data.py            # ~104 consultas secuenciales a NASA POWER (~5 min)
python scripts/fetch_data.py --limit 3  # prueba rápida con 3 celdas
```

Para forzar una descarga nueva, mové la caché correspondiente de `data/raw/` fuera del repo **antes** de correr el script. Hacé un backup: la caché es la evidencia de procedencia.

Fuentes, períodos y licencias: [`../data/SOURCES.md`](../data/SOURCES.md) y [`DATA_METHODOLOGY.md`](DATA_METHODOLOGY.md).

Para desplegar en Render, ver [`DEPLOY_RENDER.md`](DEPLOY_RENDER.md).

## 4. Problemas frecuentes
| Síntoma | Solución |
|---|---|
| `ModuleNotFoundError: fastapi` | Activá el venv y repetí `pip install -r backend/requirements.txt`. |
| `ModuleNotFoundError: backend` | Ejecutá uvicorn desde la **raíz** del repositorio. |
| El puerto 8000 está ocupado | `--port 8010` y abrí ese puerto. |
| La UI dice «DATOS SINTÉTICOS» | Falta `data/processed/cells.geojson` o está definido `INTIMAP_DATASET=sample`. |
| El asistente dice «Respuesta determinista (sin IA)» | Es el comportamiento esperado sin `LLM_API_KEY`. El motivo aparece como tooltip del indicador. |
