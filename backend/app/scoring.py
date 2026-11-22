"""Puntaje combinado — REFERENCIA matemática (PROJECT_SPEC §8).

frontend/scoring.js replica EXACTAMENTE estas funciones para que los sliders respondan sin red.
Si se cambia algo aquí, cambiarlo también allí (ver docs/DECISIONS.md, decisión 25).

  score = (w_solar·s_solar + w_wind·s_wind) / (w_solar + w_wind)

- s_solar y s_wind vienen ya normalizados 0-100 en el dataset (no se renormalizan aquí).
- Pesos de red/acceso: no existen datos reales todavía => no se aceptan.
- Si falta un componente, se usa solo el disponible re-normalizando pesos y se marca partial.
- Pesos ambos en 0 => error explícito (lo valida contracts.Weights).
"""
import math
from typing import Optional

RECOMMENDATION_MARGIN = 15  # spec §8: solar si s_solar >= s_wind + 15, etc. (se usará en Fase 3)


def normalize_weights(solar: float, wind: float) -> dict:
    total = solar + wind
    if total <= 0:
        raise ValueError("al menos un peso debe ser > 0")
    return {"solar": solar / total, "wind": wind / total}


def combined_score(s_solar: Optional[float], s_wind: Optional[float], w: dict):
    """Devuelve (score 0-100 redondeado a 1 decimal | None, partial: bool)."""
    parts = [(w["solar"], s_solar), (w["wind"], s_wind)]
    used = [(wi, si) for wi, si in parts if si is not None and wi > 0]
    if not used:
        return None, False
    total_w = sum(wi for wi, _ in used)
    score = sum(wi * si for wi, si in used) / total_w
    partial = any(si is None and wi > 0 for wi, si in parts)
    # Redondeo "half-up" igual que Math.round de JS (round() de Python redondea al par).
    return math.floor(score * 10 + 0.5) / 10, partial


def recommendation(s_solar: Optional[float], s_wind: Optional[float]) -> Optional[str]:
    """Heurística COMPARATIVA (spec §8, decisión D3): compara índices relativos, no viabilidad.

    'solar' si s_solar >= s_wind + 15; 'eolica' si s_wind >= s_solar + 15; si no, 'mixta'.
    None si falta algún índice.
    """
    if s_solar is None or s_wind is None:
        return None
    if s_solar >= s_wind + RECOMMENDATION_MARGIN:
        return "solar"
    if s_wind >= s_solar + RECOMMENDATION_MARGIN:
        return "eolica"
    return "mixta"


def rank_cells(features: list, w: dict) -> list:
    rows = []
    for f in features:
        p = f["properties"]
        score, partial = combined_score(p.get("s_solar"), p.get("s_wind"), w)
        rows.append({"id": p["id"], "solar_index": p.get("s_solar"), "wind_index": p.get("s_wind"),
                     "score": score, "partial": partial})
    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0), r["id"]))
    return rows
