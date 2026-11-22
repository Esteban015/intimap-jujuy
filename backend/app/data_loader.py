"""Carga de celdas (contrato C1). Prefiere data/processed; si no existe, usa la muestra SINTÉTICA.

Variable de entorno INTIMAP_DATASET = auto (defecto) | processed | sample.
"""
import json
import os
from functools import lru_cache
from pathlib import Path

from .indicators import min_max_0_100

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed" / "cells.geojson"
SAMPLE = ROOT / "data" / "sample" / "cells.sample.geojson"
BOUNDARY = ROOT / "data" / "processed" / "jujuy.geojson"

REQUIRED_PROPS = ("id", "centroid", "solar_ghi_kwh_m2_day", "wind_speed_50m_ms", "quality")


def _choose_path() -> Path:
    mode = os.getenv("INTIMAP_DATASET", "auto").lower()
    if mode == "sample":
        return SAMPLE
    if mode == "processed":
        if not PROCESSED.exists():
            raise FileNotFoundError(f"INTIMAP_DATASET=processed pero falta {PROCESSED}")
        return PROCESSED
    return PROCESSED if PROCESSED.exists() else SAMPLE


@lru_cache(maxsize=1)
def load_cells() -> dict:
    path = _choose_path()
    with path.open(encoding="utf-8") as f:
        fc = json.load(f)
    for feat in fc.get("features", []):
        missing = [k for k in REQUIRED_PROPS if k not in feat.get("properties", {})]
        if missing:
            raise ValueError(f"{path.name}: celda sin campos {missing}")
    meta = fc.setdefault("metadata", {})
    meta["path"] = str(path.relative_to(ROOT)).replace("\\", "/")
    # La muestra es sintética por definición: se marca aunque el archivo no lo diga.
    if path == SAMPLE:
        meta["dataset"] = "sample"
        meta["synthetic"] = True
        props = [feat["properties"] for feat in fc["features"]]
        # La muestra no trae temperatura ni altitud: sus índices se normalizan directo desde GHI y viento.
        for key, src in (("s_solar", "solar_ghi_kwh_m2_day"), ("s_wind", "wind_speed_50m_ms")):
            for p, s in zip(props, min_max_0_100(p.get(src) for p in props)):
                p.setdefault(key, s)
        for p in props:
            p["synthetic"] = True
            p["quality"] = {k: "sintetico" for k in list(p["quality"]) + ["s_solar", "s_wind"]}
    return fc


@lru_cache(maxsize=1)
def load_boundary():
    if not BOUNDARY.exists():
        return None
    return json.loads(BOUNDARY.read_text(encoding="utf-8"))


def get_cell(cell_id: str):
    for feat in load_cells()["features"]:
        if feat["properties"]["id"] == cell_id:
            return feat
    return None
