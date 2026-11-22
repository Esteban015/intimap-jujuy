"""IntiMap Jujuy — API. Dueño de endpoints: P1."""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles

from .assistant import answer
from .contracts import AssistantRequest, ScoresRequest, SimulateRequest
from .data_loader import ROOT, get_cell, load_boundary, load_cells
from .finance import simulate_solar
from .scoring import normalize_weights, rank_cells

app = FastAPI(title="IntiMap Jujuy", version="0.3.0")


@app.get("/api/health")
def health():
    fc = load_cells()
    meta = fc["metadata"]
    return {
        "status": "ok",
        "dataset": meta.get("dataset"),
        "synthetic": bool(meta.get("synthetic")),
        "data_path": meta.get("path"),
        "cells": len(fc["features"]),
        "counts": meta.get("counts"),
        "climate_period": meta.get("climate_period"),
        "boundary": load_boundary() is not None,
        "llm_required": False,
        "llm_configured": bool(os.getenv("LLM_API_KEY")),
    }


@app.get("/api/cells")
def cells(response: Response):
    fc = load_cells()
    response.headers["X-IntiMap-Dataset"] = fc["metadata"].get("dataset", "unknown")
    return fc


@app.get("/api/boundary")
def boundary():
    b = load_boundary()
    if b is None:
        raise HTTPException(status_code=404, detail="contorno no generado (ejecutar scripts/build_grid.py)")
    return b


@app.get("/api/cells/{cell_id}")
def cell(cell_id: str):
    feat = get_cell(cell_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"celda '{cell_id}' no encontrada")
    return feat


@app.post("/api/scores")
def scores(req: ScoresRequest):
    """Verificación/referencia: el frontend recalcula en el navegador con la misma fórmula."""
    w = normalize_weights(req.weights.solar, req.weights.wind)
    return {
        "weights_normalized": w,
        "method": "promedio ponderado de s_solar y s_wind (min-max 0-100 relativo a Jujuy)",
        "dataset": load_cells()["metadata"].get("dataset"),
        "cells": rank_cells(load_cells()["features"], w),
        "disclaimer": "Índice relativo entre zonas de Jujuy; no indica viabilidad, producción ni rentabilidad.",
    }


@app.get("/api/scenario")
def scenario():
    """Escenario económico HIPOTÉTICO editable (valores de ejemplo del spec, no cotizaciones)."""
    return json.loads((ROOT / "data" / "economic_scenario.json").read_text(encoding="utf-8"))


@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    feat = get_cell(req.cell_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"celda '{req.cell_id}' no encontrada")
    p = feat["properties"]
    out = simulate_solar(p.get("solar_kwh_kwp_year"), req)
    out["cell_id"] = req.cell_id
    out["solar_kwh_kwp_year"] = p.get("solar_kwh_kwp_year")
    out["synthetic"] = bool(p.get("synthetic"))
    return out


@app.post("/api/assistant")
def assistant(req: AssistantRequest):
    if req.selected_cell_id and get_cell(req.selected_cell_id) is None:
        raise HTTPException(status_code=404, detail=f"celda '{req.selected_cell_id}' no encontrada")
    return answer(load_cells(), req)


# Frontend estático (montado al final para no tapar /api)
app.mount("/", StaticFiles(directory=Path(ROOT / "frontend"), html=True), name="frontend")
