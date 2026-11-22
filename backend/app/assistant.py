"""Asistente explicativo (spec §10). Determinista por defecto; LLM opcional solo para redactar.

Contexto permitido: dataset cargado, indicadores calculados, celda seleccionada, ranking con los pesos
actuales y el escenario económico del usuario. Nada más: sin búsquedas externas ni datos inventados.

LLM (opcional): solo si existe LLM_API_KEY en el entorno del backend. Reescribe el borrador determinista;
si falla, tarda, se niega o introduce números que no están en el borrador => se devuelve el borrador.
"""
import json
import os
import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .finance import simulate_solar
from .scoring import normalize_weights, rank_cells, recommendation

MAX_WORDS = 150
LLM_TIMEOUT_S = 15.0
DEFAULT_LLM_MODEL = "claude-opus-5-5"

REC_LABEL = {"solar": "solar", "eolica": "eólica", "mixta": "mixta (solar y eólica similares)"}

# Prompt de sistema del spec §10 (tal cual) + reglas de reescritura.
SYSTEM_PROMPT = """Sos un asistente de planificación de energías renovables para la provincia de Jujuy, Argentina.
Respondé en español, de forma clara y para personas no técnicas.
Usá SOLO los datos que te paso en el contexto. No inventes cifras ni lugares.
Cada recomendación debe incluir los números que la justifican (irradiación, viento, generación estimada, retorno).
Si falta un dato o la pregunta excede lo que sabés, decilo.
Terminá siempre con una advertencia breve: son estimaciones preliminares que requieren un estudio de sitio.
Formato: 1) Recomendación, 2) Por qué, 3) Advertencia. Máximo 150 palabras.

Recibís un BORRADOR ya calculado. Reescribilo para que sea más claro. Reglas estrictas:
- No agregues, cambies ni redondees ningún número; copiá los números exactamente como aparecen en el borrador.
- No agregues localidades, red eléctrica, costos, tarifas ni producción eólica en kWh.
- Mantené los encabezados "1) Recomendación:", "2) Por qué:" y "3) Advertencia:"."""


# ---------- utilidades ----------
def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def fmt(v: Optional[float], nd: int = 0) -> str:
    """Formato es-AR: 1.234,5 — redondeo half-up (igual que la ficha del navegador)."""
    if v is None:
        return "sin dato"
    q = Decimal(str(v)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    s = f"{q:,.{nd}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def coord(p: dict) -> str:
    lat, lon = p.get("query_point") or p["centroid"]
    return f"~{fmt(abs(lat), 2)}° S, {fmt(abs(lon), 2)}° O"


def words(text: str) -> int:
    return len(text.split())


def intent_of(question: str, has_selection: bool = False) -> str:
    q = _norm(question)
    rules = [
        ("community", ("familia", "comunidad", "hogar", "vivienda", "abastec", "consumo", "pueblo", "escuela")),
        ("wind", ("eolic", "viento", "turbina", "aerogenerador", "molino")),
        ("economics", ("retorno", "recuper", "payback", "ahorro", "inversion", "costo", "rentab", "dinero", "plata", "precio")),
    ]
    if has_selection:  # "¿por qué esta zona?" con celda elegida => explicar esa celda, no el ranking
        rules.append(("explain", ("por que", "esta celda", "esta zona", "este lugar", "explic", "aca", "aqui")))
    rules.append(("where", ("donde", "mejor", "ranking", "zona", "conviene", "recomend", "top", "lugar")))
    for name, keys in rules:
        if any(k in q for k in keys):
            return name
    return "explain"


# ---------- contexto ----------
def build_context(cells_fc: dict, req) -> dict:
    w = normalize_weights(req.weights.solar, req.weights.wind)
    feats = cells_fc["features"]
    by_id = {f["properties"]["id"]: f["properties"] for f in feats}
    ranking = rank_cells(feats, w)
    rank_pos = {r["id"]: i + 1 for i, r in enumerate(ranking)}
    selected = by_id.get(req.selected_cell_id) if req.selected_cell_id else None
    target = selected or by_id[ranking[0]["id"]]
    sim = simulate_solar(target.get("solar_kwh_kwp_year"), req.scenario) if req.scenario else None
    return {
        "weights": w, "n_cells": len(feats), "synthetic": bool(cells_fc["metadata"].get("synthetic")),
        "ranking": ranking, "rank_pos": rank_pos, "by_id": by_id,
        "selected": selected, "target": target, "target_is_selected": selected is not None,
        "simulation": sim,
    }


def _cell_facts(ctx: dict, p: dict) -> dict:
    r = next(x for x in ctx["ranking"] if x["id"] == p["id"])
    return {
        "id": p["id"], "coords": coord(p), "rank": ctx["rank_pos"][p["id"]], "score": r["score"],
        "s_solar": p.get("s_solar"), "s_wind": p.get("s_wind"),
        "ghi": p.get("solar_ghi_kwh_m2_day"), "kwh_kwp": p.get("solar_kwh_kwp_year"),
        "wind": p.get("wind_speed_50m_ms"), "rho": p.get("air_density_kg_m3"),
        "wpd": p.get("wind_power_density_w_m2"), "elev": p.get("elevation_m"),
        "recommendation": recommendation(p.get("s_solar"), p.get("s_wind")),
    }


def _weights_txt(w: dict) -> str:
    return f"pesos solar {fmt(w['solar'] * 100)}% / eólico {fmt(w['wind'] * 100)}%"


def _base_warning(ctx: dict, extra: str = "") -> str:
    base = ("Datos sintéticos de demostración, no son mediciones. " if ctx["synthetic"] else "") + \
        "Estimación preliminar con datos de baja resolución (~28 km); requiere un estudio de sitio."
    return f"{base} {extra}".strip()


# ---------- respuestas deterministas ----------
def _explain(ctx: dict) -> tuple:
    f = _cell_facts(ctx, ctx["target"])
    who = "La celda seleccionada" if ctx["target_is_selected"] else "La celda mejor ubicada en el ranking"
    rec_txt = REC_LABEL.get(f["recommendation"], "no determinable (faltan índices)")
    rec = f"{who} ({f['coords']}) tiene recomendación preliminar {rec_txt}."
    why = (f"Puntaje combinado {fmt(f['score'], 1)}/100, puesto {f['rank']} de {ctx['n_cells']} con {_weights_txt(ctx['weights'])}. "
           f"Índice solar {fmt(f['s_solar'], 1)}/100: irradiación {fmt(f['ghi'], 2)} kWh/m²/día, unos {fmt(f['kwh_kwp'])} kWh por kWp al año. "
           f"Índice eólico {fmt(f['s_wind'], 1)}/100: viento medio {fmt(f['wind'], 2)} m/s a 50 m, densidad del aire {fmt(f['rho'], 3)} kg/m³. "
           "La recomendación compara índices relativos (diferencia de 15 puntos).")
    warn = _base_warning(ctx, "El índice eólico no es la energía de una turbina.")
    return rec, why, warn, f


def _where(ctx: dict) -> tuple:
    top = [_cell_facts(ctx, ctx["by_id"][r["id"]]) for r in ctx["ranking"][:3] if r["score"] is not None]
    rec = "Con las prioridades actuales, las zonas mejor puntuadas son: " + \
        "; ".join(f"{c['coords']} ({fmt(c['score'], 1)}/100)" for c in top) + "."
    t = top[0]
    why = (f"Con {_weights_txt(ctx['weights'])}, la primera tiene índice solar {fmt(t['s_solar'], 1)}/100 "
           f"({fmt(t['ghi'], 2)} kWh/m²/día, unos {fmt(t['kwh_kwp'])} kWh por kWp al año) "
           f"e índice eólico {fmt(t['s_wind'], 1)}/100 (viento {fmt(t['wind'], 2)} m/s a 50 m). "
           "Los puntajes son relativos entre las celdas de Jujuy.")
    warn = _base_warning(ctx, "No hay datos de red eléctrica, caminos ni localidades en el dataset.")
    return rec, why, warn, {"top": top}


def _wind(ctx: dict) -> tuple:
    f = _cell_facts(ctx, ctx["target"])
    best = max((ctx["by_id"][r["id"]] for r in ctx["ranking"]), key=lambda p: p.get("s_wind") or -1)
    b = _cell_facts(ctx, best)
    rec = (f"En {f['coords']} el recurso eólico relativo es {fmt(f['s_wind'], 1)}/100. "
           f"El mayor índice eólico del dataset está en {b['coords']} ({fmt(b['s_wind'], 1)}/100).")
    why = (f"Viento medio {fmt(f['wind'], 2)} m/s a 50 m y densidad del aire {fmt(f['rho'], 3)} kg/m³ "
           f"(altitud {fmt(f['elev'])} m), índice 0,5·ρ·v³ = {fmt(f['wpd'], 1)} W/m². "
           "A mayor altitud, el aire es menos denso y rinde menos potencia para el mismo viento.")
    warn = _base_warning(ctx, "No se calcula energía eólica anual: falta un modelo de turbina y la distribución de vientos.")
    return rec, why, warn, {"cell": f, "best_wind": b}


def _economics(ctx: dict) -> tuple:
    f = _cell_facts(ctx, ctx["target"])
    sim = ctx["simulation"]
    if sim is None:
        rec = "No puedo estimar el retorno sin un escenario económico."
        why = (f"En {f['coords']} cada kWp produciría unos {fmt(f['kwh_kwp'])} kWh al año (estimado). "
               "Para calcular ahorro y recuperación hacen falta potencia, costo por kWp y valor de la energía; completalos en el simulador.")
        return rec, why, _base_warning(ctx), {"cell": f}
    r, nc, i = sim["results"], sim["not_calculable"], sim["inputs"]
    pb = r["simple_payback_years"]
    pb_txt = f"unos {fmt(pb, 1)} años" if pb is not None else f"No calculable ({nc.get('simple_payback_years')})"
    rec = f"En {f['coords']}, con el escenario hipotético ingresado, la recuperación simple sería {pb_txt}."
    why = (f"{fmt(i['system_kwp'], 1)} kWp × {fmt(f['kwh_kwp'])} kWh/kWp = {fmt(r['annual_kwh'])} kWh/año; "
           f"autoconsumo {fmt(i['self_consumption_pct'])}% = {fmt(r['self_consumed_kwh'])} kWh. "
           f"Inversión {fmt(r['capex_usd'])} USD; ahorro neto {fmt(r['net_savings_usd_year'], 2)} USD/año.")
    warn = _base_warning(ctx, "Escenario editable, no cotización ni tarifa oficial; no es VAN, TIR ni rentabilidad garantizada. "
                              + " ".join(sim["warnings"][:1]))
    return rec, why, warn, {"cell": f, "simulation": r}


def _community(ctx: dict) -> tuple:
    f = _cell_facts(ctx, ctx["target"])
    rec = "No puedo afirmar si alcanza para esa comunidad: el dataset no incluye su consumo de energía."
    where = "la celda seleccionada" if ctx["target_is_selected"] else "la zona mejor puntuada con las prioridades actuales"
    why = f"En {where} ({f['coords']}) cada kWp instalado produciría unos {fmt(f['kwh_kwp'])} kWh al año (estimado). "
    sim = ctx["simulation"]
    if sim and sim["results"]["annual_kwh"] is not None:
        why += f"Con {fmt(sim['inputs']['system_kwp'], 1)} kWp del escenario serían unos {fmt(sim['results']['annual_kwh'])} kWh al año. "
    why += "Si conocen el consumo anual total en kWh, la potencia necesaria aproximada es ese consumo dividido por la producción por kWp."
    warn = _base_warning(ctx, "Faltan: consumo por hogar, horarios de uso, almacenamiento y acceso a red.")
    return rec, why, warn, {"cell": f}


HANDLERS = {"explain": _explain, "where": _where, "wind": _wind, "economics": _economics, "community": _community}


_MISSING = re.compile(r"(unos )?sin dato( (kWh/m²/día|kWh por kWp al año|kWh/kWp|kWh al año|kWh/año|kg/m³|m/s|W/m²|m|kWh))?")


def _compose(rec: str, why: str, warn: str) -> str:
    text = f"1) Recomendación: {rec}\n2) Por qué: {why}\n3) Advertencia: {warn}"
    return _MISSING.sub("sin dato", text)  # dato faltante: no adjuntar unidades ni "unos"


def _fit_words(rec: str, why: str, warn: str) -> tuple:
    """Recorta oraciones del 'Por qué' (nunca la advertencia) hasta <= MAX_WORDS. Devuelve (texto, why)."""
    sentences = re.split(r"(?<=\.)\s+", why)
    while words(_compose(rec, " ".join(sentences), warn)) > MAX_WORDS and len(sentences) > 1:
        sentences.pop()
    why = " ".join(sentences)
    return _compose(rec, why, warn), why


# ---------- LLM opcional ----------
_NUM = re.compile(r"\d[\d.,]*\d|\d")


def _numbers(text: str) -> set:
    return {n.strip(".,") for n in _NUM.findall(text)}


def _validate_llm(text: str, draft: str, question: str) -> Optional[str]:
    if words(text) > MAX_WORDS:
        return f"respuesta LLM de {words(text)} palabras (> {MAX_WORDS})"
    for h in ("1)", "2)", "3)"):
        if h not in text:
            return f"falta la sección {h}"
    extra = _numbers(text) - _numbers(draft) - _numbers(question) - {"1", "2", "3"}
    if extra:
        return f"números no presentes en los datos: {sorted(extra)[:5]}"
    return None


def _llm_rewrite(draft: str, question: str, facts: dict):
    """Devuelve (texto | None, motivo_de_fallback | None). La clave solo vive en el backend."""
    key = os.getenv("LLM_API_KEY")
    if not key:
        return None, "LLM no configurado (sin LLM_API_KEY)"
    try:
        import anthropic  # dependencia opcional: si no está instalada, se usa la respuesta determinista
    except ImportError:
        return None, "paquete anthropic no instalado"
    client = anthropic.Anthropic(api_key=key, timeout=LLM_TIMEOUT_S, max_retries=0)
    user = (f"Pregunta: {question}\n\nDatos (JSON):\n{json.dumps(facts, ensure_ascii=False, default=str)}\n\n"
            f"BORRADOR:\n{draft}")
    try:
        resp = client.beta.messages.create(
            model=os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
            max_tokens=4000,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.APITimeoutError:
        return None, "LLM excedió el tiempo"
    except anthropic.AuthenticationError:
        return None, "LLM: clave inválida"
    except anthropic.RateLimitError:
        return None, "LLM: límite de uso"
    except anthropic.APIStatusError as e:
        return None, f"LLM: error HTTP {e.status_code}"
    except anthropic.APIConnectionError:
        return None, "LLM: sin conexión"
    if resp.stop_reason != "end_turn":
        return None, f"LLM terminó con stop_reason={resp.stop_reason}"
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    problem = _validate_llm(text, draft, question)
    if problem:
        return None, f"LLM descartado: {problem}"
    return text, None


# ---------- entrada ----------
def answer(cells_fc: dict, req) -> dict:
    ctx = build_context(cells_fc, req)
    intent = intent_of(req.question, ctx["target_is_selected"])
    rec, why, warn, facts = HANDLERS[intent](ctx)
    draft, why = _fit_words(rec, why, warn)
    text, reason = _llm_rewrite(draft, req.question, facts)
    cell_ids = [c["id"] for c in facts["top"]] if "top" in facts else [ctx["target"]["id"]]
    return {
        "answer": text or draft,
        "mode": "llm" if text else "deterministic",
        "llm_fallback_reason": reason,
        "intent": intent,
        "sections": None if text else {"recommendation": rec, "justification": why, "warning": warn},
        "cell_ids": cell_ids,
        "facts_used": facts,
        "words": words(text or draft),
    }
