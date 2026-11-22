# Cómo levantar IntiMap Jujuy (Fase 0)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Linux/Mac: source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```
Abrir http://localhost:8000 (frontend) y http://localhost:8000/docs (Swagger).
Sin `.env` funciona igual: el LLM es opcional.
