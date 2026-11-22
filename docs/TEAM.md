# Reparto de trabajo (ownership de archivos, sin solapamiento)

| Persona | Perfil sugerido | Fase | Archivos que es DUEÑO de | Entrega verificable |
|---|---|---|---|---|
| P1 | Ingeniera en Computación | 2-3 | `backend/app/main.py`, `contracts.py`, `scoring.py`, `finance.py` (nuevos) | `/api/scores` y `/api/simulate` dejan de devolver 501; con solar=1 y viento=0, el ranking sigue el orden de GHI |
| P2 | Analista Programador | 2 | `frontend/*` (incluye `vendor/leaflet`) | Mapa con capas solar/viento/puntaje, sliders que recolorean y clic que abre el panel |
| P3 | Agrónoma / Analista | 3 | `backend/app/assistant.py`, `data/assumptions.json`, `docs/USE_CASES.md` | Fase 3 HECHA por el orquestador (`assistant.py` creado). PENDIENTE P3: retirar o alinear `assumptions.json` y revisar los textos agronómicos del asistente |
| P4 | QA Engineer | 1 y 4 | `scripts/*`, `data/processed/*`, `data/raw/*`, `data/SOURCES.md`, `README.md`, `docs/PITCH.md` | Fase 1 HECHA (orquestador). Smoke de cada fase y pitch |

Reglas:
- Integración solo a través de `docs/CONTRACTS.md`. Quien quiera cambiar un contrato se lo pide a P1.
- Cada uno trabaja en su propia rama (`feat/p1-scoring`, etc.). Nadie edita archivos de otro dueño.
- Mientras no exista el dataset real, todos trabajan con `data/sample/` (sintético).
- Commits, push y deploy solo con autorización del equipo.
