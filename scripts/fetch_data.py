"""Fases 1.2-1.4 — Datos climáticos por celda + indicadores preliminares.

Uso:
  python scripts/fetch_data.py              # descarga lo que falte en caché y arma el dataset
  python scripts/fetch_data.py --offline    # solo arma el dataset desde data/raw/ (sin red)
  python scripts/fetch_data.py --limit 3    # prueba con pocas celdas

Entrada: data/processed/grid.geojson (scripts/build_grid.py)
Caché:   data/raw/nasa_power/<id>.json, data/raw/open_meteo_elevation.json
Salida:  data/processed/cells.geojson (contrato C1 v1, docs/CONTRACTS.md)

Reglas: consultas secuenciales con pausa; timeout y reintentos; un fallo deja el campo en null con
estado "faltante" (NUNCA se rellena con datos sintéticos).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.indicators import (air_density_kg_m3, min_max_0_100,  # noqa: E402
                                    solar_kwh_per_kwp_year, wind_power_density_w_m2)

RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
POWER_DIR = RAW / "nasa_power"
ELEV_CACHE = RAW / "open_meteo_elevation.json"
TIMEOUT_S = 60
PAUSE_S = 1.0
RETRIES = 2

POWER_PARAMS = ["ALLSKY_SFC_SW_DWN", "T2M", "WS50M"]
POWER_URL = ("https://power.larc.nasa.gov/api/temporal/climatology/point"
             "?parameters={params}&community=RE&longitude={lon}&latitude={lat}&format=JSON")
ELEV_URL = "https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"
WIND_HEIGHT_M = 50

SOURCES = [
    {"id": "nasa_power", "name": "NASA POWER — Climatology API (comunidad RE)",
     "url": "https://power.larc.nasa.gov/docs/services/api/temporal/climatology/",
     "terms": "Datos públicos de NASA; citar según https://power.larc.nasa.gov/docs/referencing/",
     "native_resolution": "solar ~1°×1°, meteorología MERRA-2 ~0,5°×0,625°: celdas vecinas de 0,25° pueden compartir valor"},
    {"id": "open_meteo_elevation", "name": "Open-Meteo Elevation API (Copernicus DEM GLO-90, 90 m)",
     "url": "https://open-meteo.com/en/docs/elevation-api",
     "terms": "Gratuito para uso NO comercial (https://open-meteo.com/en/terms); atribución CC BY 4.0. "
              "Uso comercial requiere plan pago."},
]

VARIABLES = {
    "solar_ghi_kwh_m2_day": {"unit": "kWh/m²/día", "source": "nasa_power", "param": "ALLSKY_SFC_SW_DWN",
                             "desc": "Irradiación global horizontal, media anual"},
    "temp_mean_c": {"unit": "°C", "source": "nasa_power", "param": "T2M", "desc": "Temperatura media anual a 2 m"},
    "wind_speed_50m_ms": {"unit": "m/s", "source": "nasa_power", "param": "WS50M", "height_m": WIND_HEIGHT_M,
                          "desc": "Velocidad media anual del viento a 50 m"},
    "elevation_m": {"unit": "m s.n.m.", "source": "open_meteo_elevation",
                    "desc": "Altitud del punto de consulta (DEM 90 m; no representa toda la celda)"},
    "solar_kwh_kwp_year": {"unit": "kWh/kWp/año", "derived": "GHI·365·0,80·(1−0,004·(Tamb+20−25))",
                           "desc": "Generación FV específica estimada"},
    "air_density_kg_m3": {"unit": "kg/m³", "derived": "1,225·(1−2,25577e-5·h)^4,25588",
                          "desc": "Densidad del aire aproximada por altitud (atmósfera estándar)"},
    "wind_power_density_w_m2": {"unit": "W/m²", "derived": "0,5·ρ·v³ con v media",
                                "desc": "Índice de recurso eólico; subestima la densidad real y NO es energía de turbina"},
    "s_solar": {"unit": "0-100", "derived": "min-max de solar_kwh_kwp_year entre celdas con dato",
                "desc": "Índice relativo dentro de Jujuy; no certifica viabilidad"},
    "s_wind": {"unit": "0-100", "derived": "min-max de wind_power_density_w_m2 entre celdas con dato",
               "desc": "Índice relativo dentro de Jujuy; no certifica viabilidad"},
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def http_json(url: str) -> dict:
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "intimap-hackathon-script"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{type(last).__name__}: {last}")


def fetch_power(cell_id: str, lat: float, lon: float, offline: bool):
    cache = POWER_DIR / f"{cell_id}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8")), None
    if offline:
        return None, "sin caché (offline)"
    url = POWER_URL.format(params=",".join(POWER_PARAMS), lat=lat, lon=lon)
    try:
        data = http_json(url)
    except RuntimeError as e:
        return None, str(e)
    payload = {"fetched_at": now_iso(), "url": url, "response": data}
    POWER_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(payload), encoding="utf-8")
    time.sleep(PAUSE_S)
    return payload, None


def fetch_elevations(points: dict, offline: bool) -> dict:
    """points: {cell_id: (lat, lon)}. Lotes de hasta 100 coordenadas por solicitud."""
    cache = json.loads(ELEV_CACHE.read_text(encoding="utf-8")) if ELEV_CACHE.exists() else {}
    missing = [cid for cid in points if cid not in cache]
    if missing and not offline:
        for i in range(0, len(missing), 100):
            batch = missing[i:i + 100]
            url = ELEV_URL.format(lats=",".join(str(points[c][0]) for c in batch),
                                  lons=",".join(str(points[c][1]) for c in batch))
            try:
                elev = http_json(url)["elevation"]
            except (RuntimeError, KeyError) as e:
                print(f"AVISO Open-Meteo lote {i // 100}: {e}")
                continue
            ts = now_iso()
            for cid, h in zip(batch, elev):
                cache[cid] = {"elevation_m": h, "fetched_at": ts, "point": list(points[cid])}
            time.sleep(PAUSE_S)
        RAW.mkdir(parents=True, exist_ok=True)
        ELEV_CACHE.write_text(json.dumps(cache, indent=0), encoding="utf-8")
    return cache


def parse_power(payload):
    """Devuelve (valores, período, error). Valores fill (-999) => None."""
    resp = payload["response"]
    fill = resp.get("header", {}).get("fill_value", -999.0)
    params = resp.get("properties", {}).get("parameter", {})
    units = resp.get("parameters", {})
    expected = {"ALLSKY_SFC_SW_DWN": "kW-hr/m^2/day", "T2M": "C", "WS50M": "m/s"}
    out = {}
    for p, unit in expected.items():
        got = units.get(p, {}).get("units")
        if got != unit:
            return None, None, f"unidad inesperada para {p}: {got!r}"
        v = params.get(p, {}).get("ANN")
        out[p] = None if v is None or v == fill else float(v)
    return out, resp.get("header", {}).get("range"), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    grid = json.loads((OUT / "grid.geojson").read_text(encoding="utf-8"))
    feats = grid["features"][: args.limit or None]
    points = {f["properties"]["id"]: tuple(f["properties"]["query_point"]) for f in feats}

    elevs = fetch_elevations(points, args.offline)
    errors, periods = [], set()
    for i, f in enumerate(feats, 1):
        p = f["properties"]
        lat, lon = p["query_point"]
        payload, err = fetch_power(p["id"], lat, lon, args.offline)
        vals, period = {}, None
        if payload:
            vals, period, err = parse_power(payload)
            vals = vals or {}
        if err:
            errors.append(f"{p['id']} NASA POWER: {err}")
        if period:
            periods.add(period)
        e = elevs.get(p["id"])
        ghi, t2m, ws = vals.get("ALLSKY_SFC_SW_DWN"), vals.get("T2M"), vals.get("WS50M")
        h = e["elevation_m"] if e else None
        if e is None:
            errors.append(f"{p['id']} Open-Meteo: altitud faltante")
        rho = air_density_kg_m3(h)
        p.update({
            "solar_ghi_kwh_m2_day": ghi, "temp_mean_c": t2m, "wind_speed_50m_ms": ws,
            "wind_height_m": WIND_HEIGHT_M, "elevation_m": h,
            "solar_kwh_kwp_year": _r(solar_kwh_per_kwp_year(ghi, t2m), 0),
            "air_density_kg_m3": _r(rho, 3),
            "wind_power_density_w_m2": _r(wind_power_density_w_m2(ws, rho), 1),
            "synthetic": False,
            "quality": {
                "solar_ghi_kwh_m2_day": "real" if ghi is not None else "faltante",
                "temp_mean_c": "real" if t2m is not None else "faltante",
                "wind_speed_50m_ms": "real" if ws is not None else "faltante",
                "elevation_m": "real" if h is not None else "faltante",
                "solar_kwh_kwp_year": "estimado" if ghi is not None and t2m is not None else "faltante",
                "air_density_kg_m3": "estimado" if h is not None else "faltante",
                "wind_power_density_w_m2": "estimado" if ws is not None and h is not None else "faltante",
            },
            "provenance": {
                "nasa_power": {"fetched_at": payload["fetched_at"], "period": period} if payload else None,
                "open_meteo_elevation": {"fetched_at": e["fetched_at"]} if e else None,
            },
        })
        if i % 10 == 0 or i == len(feats):
            print(f"  {i}/{len(feats)} celdas procesadas")

    for key, src in (("s_solar", "solar_kwh_kwp_year"), ("s_wind", "wind_power_density_w_m2")):
        for f, s in zip(feats, min_max_0_100(f["properties"][src] for f in feats)):
            f["properties"][key] = s
            f["properties"]["quality"][key] = "estimado" if s is not None else "faltante"

    complete = sum(all(q in ("real", "estimado") for q in f["properties"]["quality"].values()) for f in feats)
    out = {
        "type": "FeatureCollection",
        "metadata": {
            "dataset": "processed", "synthetic": False, "generated_at": now_iso(),
            "grid_resolution_deg": grid["metadata"]["grid_resolution_deg"],
            "boundary_source": grid["metadata"]["boundary_source"],
            "climate_period": sorted(periods), "sources": SOURCES, "variables": VARIABLES,
            "counts": {"cells": len(feats), "complete": complete, "with_missing": len(feats) - complete},
            "disclaimer": "Estimaciones preliminares para prefactibilidad. No reemplazan un estudio de sitio.",
        },
        "features": feats,
    }
    (OUT / "cells.geojson").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"cells.geojson: {len(feats)} celdas, {complete} completas, {len(feats) - complete} con faltantes")
    for e in errors:
        print("FALTANTE:", e)


def _r(v, nd):
    return None if v is None else round(v, nd)


if __name__ == "__main__":
    main()
