# Despliegue en Render — IntiMap Jujuy

IntiMap se despliega como **un único Web Service**: FastAPI sirve la API (`/api/*`) y el frontend estático (`/`) desde el mismo dominio. No necesita base de datos, disco persistente, secretos ni APIs climáticas en ejecución. El dataset procesado viaja en el repositorio.

> Todavía **no existe ninguna URL pública**. Este documento describe cómo crearla.

## Configuración (incluida en el repositorio)

| Archivo | Propósito |
|---|---|
| `render.yaml` | Blueprint con el servicio `intimap-jujuy` (web, Python, plan free, health check `/api/health`). |
| `.python-version` | Fija Python **3.13**, la versión con que se validó el MVP. Sin este archivo, Render usa por defecto 3.14.x para servicios nuevos. |
| `backend/requirements.txt` | Versiones fijadas: fastapi 0.165.0, uvicorn 0.54.0, pydantic 2.14.4, starlette 1.10.0 y anthropic 2.12.0. El SDK anthropic es opcional en ejecución. |

| Parámetro | Valor |
|---|---|
| **Build command** | `pip install -r backend/requirements.txt` |
| **Start command** | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| **Health check** | `/api/health` |
| **Root directory** | La raíz del repo (vacío). |

### Variables de entorno
| Variable | Valor | ¿Requerida? | Motivo |
|---|---|---|---|
| `INTIMAP_DATASET` | `processed` | Recomendada (ya está en `render.yaml`) | Si faltara el dataset real, el servicio **falla** (health devuelve 500) en lugar de servir la muestra sintética sin avisar. |
| `PORT` | La provee Render (por defecto 10000) | Automática | No hay que definirla. |
| `LLM_API_KEY` | — | **No** (omitida a propósito) | Sin ella, el asistente responde en modo determinista. Si alguna vez se activa, se carga como secreto en el dashboard, **nunca** en `render.yaml`. |
| `LLM_MODEL` | — | No | Solo aplica si hay `LLM_API_KEY`. |

## Pasos

### Opción A — Blueprint (recomendada, usa `render.yaml`)
1. Fusionar en `main` el PR que agrega `render.yaml` y `.python-version`. El Blueprint despliega la rama `main`.
2. En https://dashboard.render.com: **New → Blueprint**.
3. Conectar la cuenta de GitHub **Esteban015** y elegir `Esteban015/intimap-jujuy`. Si el repo es privado, hay que darle acceso a la GitHub App de Render.
4. Render detecta `render.yaml` y muestra el servicio `intimap-jujuy` con plan **Free**. Revisar que diga *Free* y **Apply**.
5. Esperar el build (`pip install`) y el deploy. El servicio queda «Live» cuando `/api/health` responde 200.
6. Abrir la URL asignada (`https://<nombre>.onrender.com`) y correr el smoke de la sección siguiente.

### Opción B — Web Service manual
**New → Web Service** → elegir el repo, rama `main`, *Language* Python 3 y luego:
- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Instance type: **Free**
- Advanced → Health Check Path: `/api/health`
- Environment: `INTIMAP_DATASET=processed`

`.python-version` se aplica igual.

## Smoke después del deploy
Reemplazar `URL` por la dirección asignada:
```bash
URL=https://<nombre>.onrender.com
curl -s $URL/api/health          # "dataset":"processed", "cells":104, "llm_configured":false
curl -s $URL/api/cells | python -c "import json,sys;print(len(json.load(sys.stdin)['features']))"   # 104
curl -s -o /dev/null -w "%{http_code}\n" $URL/api/boundary   # 200
curl -s -X POST $URL/api/simulate -H "Content-Type: application/json" \
  -d '{"cell_id":"c_-23.375_-67.125","system_kwp":5,"cost_per_kwp_usd":900,"energy_value_usd_kwh":0.1,"self_consumption_pct":80}'
# simple_payback_years: 5.2
```
En el navegador: el mapa muestra 104 celdas, los sliders recolorean, el simulador calcula y el asistente responde «Respuesta determinista (sin IA)».

## Limitaciones del plan Free (según la documentación de Render)
- **Se apaga tras 15 minutos sin tráfico** y tarda **alrededor de 1 minuto** en volver. Para una demo, **abrir la URL unos minutos antes** de presentar.
- 750 horas de instancia gratis por mes y por workspace (el tiempo apagado no cuenta).
- Sistema de archivos efímero, que no afecta: la app solo lee datos del repo.
- Render puede reiniciar servicios free en cualquier momento y no los recomienda para producción.
- **Plan B de la demo:** correr la app local (`docs/SETUP.md`), que funciona sin internet.

## Consideraciones de un sitio público
- **No hay autenticación ni límites de uso** (fuera del alcance del MVP). Los endpoints son de solo lectura o cálculo y no guardan datos.
- `/docs` (Swagger) queda público. Solo describe la API.
- **Visibilidad del repo:** Render puede desplegar un repo privado si se le da acceso.
- **Licencias de datos en un sitio público:** Open-Meteo (altitud) es solo para uso **no comercial**, con atribución CC BY 4.0. La demo del hackatón entra en ese uso; un uso comercial requiere reemplazar la fuente. El contorno del IGN requiere atribución y sus términos exactos están a confirmar. La interfaz ya muestra las atribuciones.
- **Sin secretos:** el Blueprint no contiene claves y `LLM_API_KEY` no está configurada.

## Qué se verificó localmente (simulando producción)
Se usó una copia limpia que contiene solo los archivos versionados (sin `.cursor/`), un venv nuevo con las versiones fijadas y el **start command exacto**, con `PORT=10000`, `INTIMAP_DATASET=processed` y sin `LLM_API_KEY`:
- **Build:** `pip install` limpio y `pip check` sin conflictos. Python 3.13.14 en Windows: no se pudo probar en Linux porque no había Docker ni WSL. Para compensar, se verificó con `git ls-files` que todas las rutas coinciden exactamente en mayúsculas y minúsculas.
- **Binding:** `Uvicorn running on http://0.0.0.0:10000` y respuesta también por la IP de red de la máquina.
- **API:**
  - `/api/health` 200 (`processed`, 104 celdas, `llm_configured:false`).
  - `/api/cells` con 104 features y header `X-IntiMap-Dataset: processed`.
  - `/api/boundary` 200.
- **Frontend:** `/`, los JS, los CSS, Leaflet y `/docs` responden 200.
- **Cálculos:**
  - `/api/simulate` da una recuperación de 5,2 años; una potencia 0 devuelve 422.
  - `/api/assistant` responde en modo `deterministic`.
- **Navegador (Chrome):** 104 celdas, capas, sliders sin requests, simulador y asistente, con 0 errores de consola y 0 requests externos.
- **Directorio de trabajo:** arrancado desde otra carpeta (`--app-dir`), carga los mismos datos y el mismo frontend.
- **Dataset ausente:** con `INTIMAP_DATASET=processed`, el health devuelve 500 con `FileNotFoundError` explícito.
- **`render.yaml`:** se parsea con un parser YAML real y tiene las claves esperadas.
