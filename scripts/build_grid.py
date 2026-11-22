"""Fase 1.1 — Contorno de Jujuy + grilla de 0,25° recortada.

Uso:  python scripts/build_grid.py [--offline]
Salida: data/processed/jujuy.geojson, data/processed/grid.geojson
Caché:  data/raw/boundary_*.json (respuesta original + metadatos de descarga)

Fuente primaria: IGN Argentina (WFS oficial, capa ign:provincia).
Respaldo: geoBoundaries gbOpen ARG ADM1 (origen Wikimedia, NO oficial) — se marca como tal.
Nunca se fabrica un contorno: si ninguna fuente ni caché está disponible, el script falla.
"""
import argparse
import json
import math
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
CELL_DEG = 0.25
KM_PER_DEG = 111.32
TIMEOUT_S = 60

SOURCES = [
    {
        "id": "ign_wfs",
        "name": "Instituto Geográfico Nacional (IGN) — capa ign:provincia (WFS)",
        "url": ("https://wms.ign.gob.ar/geoserver/ign/ows?service=WFS&version=2.0.0&request=GetFeature"
                "&typeNames=ign:provincia&outputFormat=application/json&CQL_FILTER=nam%3D%27Jujuy%27"),
        "official": True,
        "license": "Licencia de uso del IGN (https://www.ign.gob.ar/NuestrasActividades/InformacionGeoespacial/CapasSIG); "
                   "requiere atribución al IGN. Términos exactos A CONFIRMAR.",
        "pick": lambda f: f["properties"].get("nam") == "Jujuy",
    },
    {
        "id": "geoboundaries",
        "name": "geoBoundaries gbOpen ARG ADM1 (origen Wikimedia, año 2006) — RESPALDO NO OFICIAL",
        "url": "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ARG/ADM1/geoBoundaries-ARG-ADM1_simplified.geojson",
        "official": False,
        "license": "CC BY 2.5 (según metadatos de geoBoundaries)",
        "pick": lambda f: "jujuy" in str(f["properties"].get("shapeName", "")).lower(),
    },
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "intimap-hackathon-script"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.load(r)


def load_boundary(offline: bool):
    """Devuelve (geometría, metadatos de fuente). Prueba fuente primaria, luego respaldo; usa caché."""
    RAW.mkdir(parents=True, exist_ok=True)
    errors = []
    for src in SOURCES:
        cache = RAW / f"boundary_{src['id']}.json"
        if cache.exists():
            payload = json.loads(cache.read_text(encoding="utf-8"))
        elif offline:
            errors.append(f"{src['id']}: sin caché (modo offline)")
            continue
        else:
            try:
                data = fetch_json(src["url"])
            except Exception as e:  # red, timeout, JSON inválido
                errors.append(f"{src['id']}: {type(e).__name__}: {e}")
                continue
            feats = [f for f in data.get("features", []) if src["pick"](f)]
            if not feats:
                errors.append(f"{src['id']}: respuesta sin feature de Jujuy")
                continue
            payload = {
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "url": src["url"],
                "feature": feats[0],
            }
            cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        geom = make_valid(shape(payload["feature"]["geometry"]))
        meta = {k: v for k, v in src.items() if k != "pick"}
        meta["fetched_at"] = payload["fetched_at"]
        return geom, meta, errors
    sys.exit("ERROR: no se pudo obtener el contorno de Jujuy de ninguna fuente:\n  " + "\n  ".join(errors))


def approx_area_km2(geom) -> float:
    """Área aproximada: grados² escalados por cos(latitud del centroide)."""
    lat = geom.centroid.y
    return geom.area * KM_PER_DEG ** 2 * math.cos(math.radians(lat))


def build_grid(province):
    minx, miny, maxx, maxy = province.bounds
    x0 = math.floor(minx / CELL_DEG) * CELL_DEG
    y0 = math.floor(miny / CELL_DEG) * CELL_DEG
    ncols = math.ceil((maxx - x0) / CELL_DEG)
    nrows = math.ceil((maxy - y0) / CELL_DEG)
    feats = []
    for r in range(nrows):
        for c in range(ncols):
            lon0, lat0 = x0 + c * CELL_DEG, y0 + r * CELL_DEG
            square = box(lon0, lat0, lon0 + CELL_DEG, lat0 + CELL_DEG)
            if not square.intersects(province):
                continue
            clipped = square.intersection(province)
            if clipped.is_empty or clipped.area == 0:
                continue
            clat, clon = lat0 + CELL_DEG / 2, lon0 + CELL_DEG / 2
            # Punto de consulta climática: centroide del recorte si cae dentro, si no un punto interior.
            qp = clipped.centroid if clipped.contains(clipped.centroid) else clipped.representative_point()
            feats.append({
                "type": "Feature",
                "geometry": mapping(clipped),
                "properties": {
                    "id": f"c_{clat:.3f}_{clon:.3f}",
                    "centroid": [round(clat, 3), round(clon, 3)],
                    "query_point": [round(qp.y, 4), round(qp.x, 4)],
                    "area_km2": round(approx_area_km2(clipped), 1),
                    "coverage_fraction": round(clipped.area / square.area, 3),
                },
            })
    return feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="usar solo la caché de data/raw/")
    args = ap.parse_args()

    province, src, errors = load_boundary(args.offline)
    for e in errors:
        print("AVISO fuente de contorno:", e)
    print(f"Contorno: {src['name']} (oficial={src['official']})")

    OUT.mkdir(parents=True, exist_ok=True)
    simplified = province.simplify(0.002, preserve_topology=True)  # ~200 m, para dibujar
    (OUT / "jujuy.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {"source": src, "simplified_tolerance_deg": 0.002,
                     "area_km2_approx": round(approx_area_km2(province), 0)},
        "features": [{"type": "Feature", "geometry": mapping(simplified), "properties": {"name": "Jujuy"}}],
    }, ensure_ascii=False), encoding="utf-8")

    cells = build_grid(province)
    union = unary_union([shape(f["geometry"]) for f in cells])
    coverage = union.area / province.area
    (OUT / "grid.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {"boundary_source": src, "grid_resolution_deg": CELL_DEG,
                     "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "area_method": "aproximada: grados² × 111,32² × cos(lat)"},
        "features": cells,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"Celdas: {len(cells)} · cobertura de la provincia por la grilla: {coverage:.4f}")


if __name__ == "__main__":
    main()
