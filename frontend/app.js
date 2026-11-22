// IntiMap Jujuy — mapa, capas, prioridades y ficha (Fase 2). Sin llamadas a APIs externas:
// solo /api/cells y /api/boundary al cargar; los sliders recalculan en el navegador (scoring.js).
(function () {
  "use strict";
  const S = window.IntiScoring;

  // Escala rojo-amarillo-verde (ColorBrewer RdYlGn, 5 clases) para índices 0-100.
  const BINS = [
    { max: 20, color: "#d73027", label: "0–20 · muy bajo" },
    { max: 40, color: "#fc8d59", label: "20–40 · bajo" },
    { max: 60, color: "#fee08b", label: "40–60 · medio" },
    { max: 80, color: "#91cf60", label: "60–80 · alto" },
    { max: 100.0001, color: "#1a9850", label: "80–100 · muy alto" },
  ];
  const NO_DATA = "#b8bec6";
  const LAYER_NAMES = {
    score: "Puntaje combinado (0–100)",
    s_solar: "Potencial solar relativo (0–100)",
    s_wind: "Recurso eólico relativo (0–100)",
  };
  const QUALITY_LABEL = { real: "descargado", estimado: "calculado", sintetico: "sintético", faltante: "faltante" };
  const REC_LABEL = { solar: "Solar", eolica: "Eólica", mixta: "Mixta (índices similares)" };

  const state = { layer: "score", weights: null, scores: new Map(), cells: [], meta: {}, selectedId: null, layersById: new Map() };
  const $ = (id) => document.getElementById(id);

  function colorFor(v) {
    if (v == null) return NO_DATA;
    return BINS.find((b) => v < b.max).color;
  }
  const fmt = (v, d = 1, unit = "") =>
    v == null ? "—" : `${Number(v).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d })}${unit ? " " + unit : ""}`;

  // ---------- Mapa ----------
  const map = L.map("map", { zoomSnap: 0.25, preferCanvas: false, attributionControl: true });
  map.attributionControl.setPrefix(false);
  let baseLayer = null;
  $("basemap").addEventListener("change", (e) => {
    if (e.target.checked) {
      baseLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 12, attribution: "© OpenStreetMap",
      }).addTo(map);
      baseLayer.bringToBack();
    } else if (baseLayer) {
      map.removeLayer(baseLayer);
      baseLayer = null;
    }
  });

  function valueOf(id) {
    const p = state.byId.get(id);
    return state.layer === "score" ? state.scores.get(id)?.score ?? null : p[state.layer] ?? null;
  }

  function styleFor(id) {
    const selected = id === state.selectedId;
    return {
      fillColor: colorFor(valueOf(id)), fillOpacity: 0.78,
      color: selected ? "#111" : "#ffffff", weight: selected ? 3 : 0.6, opacity: 1,
    };
  }

  function restyleAll() {
    state.layersById.forEach((lyr, id) => lyr.setStyle(styleFor(id)));
    const sel = state.layersById.get(state.selectedId);
    if (sel) sel.bringToFront();
  }

  function renderLegend() {
    const bar = BINS.map((b) => `<span class="seg" style="background:${b.color}" title="${b.label}"></span>`).join("");
    $("legend").innerHTML = `<div class="title">${LAYER_NAMES[state.layer]}</div>
      <div class="bar">${bar}</div>
      <div class="ticks"><span>0</span><span>20</span><span>40</span><span>60</span><span>80</span><span>100</span></div>
      <div class="ends"><span>bajo</span><span>alto</span></div>
      <div class="row"><span class="sw" style="background:${NO_DATA}"></span>sin dato / sin pesos</div>
      <div class="muted">Relativo entre celdas de Jujuy. No es viabilidad ni producción.</div>`;
  }

  // ---------- Puntajes y ranking ----------
  function recompute() {
    const ws = Number($("w-solar").value), ww = Number($("w-wind").value);
    state.weights = S.normalizeWeights(ws, ww);
    $("w-solar-out").textContent = state.weights ? `${Math.round(state.weights.solar * 100)}%` : "0%";
    $("w-wind-out").textContent = state.weights ? `${Math.round(state.weights.wind * 100)}%` : "0%";
    $("weights-warning").hidden = !!state.weights;

    const ranking = S.rankCells(state.cells, state.weights);
    state.scores = new Map(ranking.map((r) => [r.id, r]));
    state.ranking = ranking;
    renderRanking();
    restyleAll();
    if (state.selectedId) renderCard(state.selectedId);
  }

  function renderRanking() {
    const ol = $("ranking");
    if (!state.weights) {
      ol.innerHTML = '<li class="muted">Sin pesos: ranking no disponible.</li>';
      return;
    }
    ol.innerHTML = state.ranking.slice(0, 5).map((r) => {
      const p = state.byId.get(r.id);
      return `<li><button type="button" data-id="${r.id}">${fmt(r.score)} · ${coordLabel(p)}</button></li>`;
    }).join("");
    ol.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => select(b.dataset.id, true)));
  }

  function coordLabel(p) {
    const [lat, lon] = p.query_point || p.centroid;
    return `~${fmt(Math.abs(lat), 2)}° S, ${fmt(Math.abs(lon), 2)}° O`;
  }

  // ---------- Ficha ----------
  function tag(q) {
    return q ? `<span class="tag ${q}" title="Calidad del dato">${QUALITY_LABEL[q] || q}</span>` : "";
  }
  function row(label, value, q) {
    return `<tr><th>${label}</th><td>${value}${tag(q)}</td></tr>`;
  }

  function renderCard(id) {
    const p = state.byId.get(id);
    const q = p.quality || {};
    const sc = state.scores.get(id);
    const rank = state.weights ? state.ranking.findIndex((r) => r.id === id) + 1 : null;
    const synthetic = p.synthetic ? '<p class="warning">Celda con DATOS SINTÉTICOS de demostración: no son mediciones.</p>' : "";
    const [lat, lon] = p.query_point || p.centroid;
    $("card").innerHTML = `
      <h2>Ficha de la celda</h2>
      ${synthetic}
      <div><span class="scorebig">${state.weights ? fmt(sc?.score) : "—"}</span> <span class="muted">/ 100 puntaje combinado</span></div>
      <p class="muted">${state.weights ? `Puesto ${rank} de ${state.cells.length} con los pesos actuales${sc?.partial ? " (parcial: falta un componente)" : ""}.` : "Sin pesos: puntaje combinado no calculado."}</p>
      <table>
        <tr class="group"><th colspan="2">Ubicación</th></tr>
        ${row("Identificador", `<code>${p.id}</code>`)}
        ${row("Punto representativo", `${lat.toFixed(3)}, ${lon.toFixed(3)}`)}
        ${p.area_km2 != null ? row("Superficie en Jujuy (aprox.)", fmt(p.area_km2, 0, "km²")) : ""}
        ${p.coverage_fraction != null && p.coverage_fraction < 1 ? row("Celda de borde", `${fmt(p.coverage_fraction * 100, 0)}% dentro de Jujuy`) : ""}

        <tr class="group"><th colspan="2">${p.synthetic ? "Datos de entrada (sintéticos, no descargados)" : "Datos descargados"}</th></tr>
        ${row("Irradiación global (GHI)", fmt(p.solar_ghi_kwh_m2_day, 2, "kWh/m²/día"), q.solar_ghi_kwh_m2_day)}
        ${row("Temperatura media", fmt(p.temp_mean_c, 1, "°C"), q.temp_mean_c)}
        ${row(`Viento medio a ${p.wind_height_m ?? 50} m`, fmt(p.wind_speed_50m_ms, 2, "m/s"), q.wind_speed_50m_ms)}
        ${row("Altitud del punto", fmt(p.elevation_m, 0, "m s.n.m."), q.elevation_m)}

        <tr class="group"><th colspan="2">Indicadores calculados</th></tr>
        ${row("Densidad del aire (aprox.)", fmt(p.air_density_kg_m3, 3, "kg/m³"), q.air_density_kg_m3)}
        ${row("Generación solar aprox.", fmt(p.solar_kwh_kwp_year, 0, "kWh/kWp/año"), q.solar_kwh_kwp_year)}
        ${row("Índice de recurso eólico", fmt(p.wind_power_density_w_m2, 1, "W/m²"), q.wind_power_density_w_m2)}
        ${row("Índice solar relativo", fmt(p.s_solar, 1, "/ 100"), q.s_solar)}
        ${row("Índice eólico relativo", fmt(p.s_wind, 1, "/ 100"), q.s_wind)}
        <tr class="group"><th colspan="2">Recomendación preliminar</th></tr>
        <tr><td colspan="2" style="text-align:left"><span class="rec">${REC_LABEL[S.recommendation(p.s_solar, p.s_wind)] || "No determinable (faltan índices)"}</span></td></tr>
      </table>
      <p class="muted">Recomendación = heurística comparativa: solar si su índice supera al eólico por 15 puntos o más, eólica a la inversa, mixta si no. No certifica viabilidad.
      El índice eólico (0,5·ρ·v³ con viento medio) compara recurso entre zonas; <strong>no</strong> es la energía que produciría una turbina.
      La generación solar es una aproximación (PR 0,80 y corrección por temperatura).</p>
      <p class="muted">Fuentes: ${sourceLine()}.</p>`;
  }

  function sourceLine() {
    if (state.meta.synthetic) return "datos sintéticos de demostración (sin fuente real)";
    const period = (state.meta.climate_period || [])[0] || "";
    const years = period.match(/(\d{4})\D+(\d{4})/);
    return `NASA POWER (climatología ${years ? `${years[1]}–${years[2]}` : "histórica"}), Open-Meteo/Copernicus DEM (altitud), contorno IGN`;
  }

  function select(id, pan) {
    const prev = state.selectedId;
    state.selectedId = id;
    if (prev && state.layersById.get(prev)) state.layersById.get(prev).setStyle(styleFor(prev));
    const lyr = state.layersById.get(id);
    lyr.setStyle(styleFor(id));
    lyr.bringToFront();
    if (pan) map.panTo(lyr.getBounds().getCenter());
    renderCard(id);
    $("sim").hidden = false;
    scheduleSimulation(0);
  }

  // ---------- Simulador solar (cálculo en backend/app/finance.py, única implementación) ----------
  const SIM_FIELDS = ["system_kwp", "cost_per_kwp_usd", "energy_value_usd_kwh", "self_consumption_pct", "om_usd_year", "export_value_usd_kwh"];
  const OPTIONAL = new Set(["cost_per_kwp_usd", "energy_value_usd_kwh", "om_usd_year", "export_value_usd_kwh"]);
  let simTimer = null, simSeq = 0;

  /** Lee y valida el formulario. Devuelve {scenario} o {error}. Vacío en opcionales = no informado (null). */
  function readScenario() {
    const f = $("sim-form").elements, s = {};
    for (const k of SIM_FIELDS) {
      const raw = f[k].value.trim();
      if (raw === "") {
        if (OPTIONAL.has(k)) { s[k] = null; continue; }
        return { error: `Completá "${f[k].closest("label").firstChild.textContent.trim()}".` };
      }
      const v = Number(raw);
      if (!Number.isFinite(v)) return { error: "Hay un valor que no es numérico." };
      s[k] = v;
    }
    if (!(s.system_kwp > 0)) return { error: "La potencia instalada debe ser mayor a 0 kWp." };
    if (s.self_consumption_pct < 0 || s.self_consumption_pct > 100) return { error: "El autoconsumo debe estar entre 0 y 100 %." };
    for (const k of OPTIONAL) if (s[k] != null && s[k] < 0) return { error: "Costos y tarifas no pueden ser negativos." };
    return { scenario: s };
  }

  function scheduleSimulation(delay = 250) {
    clearTimeout(simTimer);
    simTimer = setTimeout(runSimulation, delay);
  }

  async function runSimulation() {
    if (!state.selectedId) return;
    const { scenario, error } = readScenario();
    const errEl = $("sim-error");
    if (error) {  // nunca mostrar resultados de un escenario inválido
      errEl.textContent = error; errEl.hidden = false; $("sim-out").innerHTML = "";
      return;
    }
    errEl.hidden = true;
    const seq = ++simSeq;
    $("sim-out").innerHTML = '<p class="muted">Calculando…</p>';
    try {
      const res = await fetch("/api/simulate", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cell_id: state.selectedId, ...scenario }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      if (seq === simSeq) renderSimulation(d);
    } catch (e) {
      if (seq === simSeq) $("sim-out").innerHTML = `<p class="warning">No se pudo simular: ${e.message}</p>`;
    }
  }

  function money(v, d = 0) { return fmt(v, d, "USD"); }
  function ncOr(d, key, text) {
    return d.results[key] == null ? `<span class="nc" title="${d.not_calculable[key] || ""}">No calculable</span>` : text;
  }

  function renderSimulation(d) {
    const r = d.results, i = d.inputs;
    const payback = ncOr(d, "simple_payback_years", `${fmt(r.simple_payback_years, 1)} años`);
    const reasons = Object.entries(d.not_calculable).map(([k, v]) => `<li>${v}</li>`).join("");
    $("sim-out").innerHTML = `
      ${d.synthetic ? '<p class="warning">Celda sintética: resultados solo ilustrativos.</p>' : ""}
      <table>
        ${row("Generación solar anual aprox.", ncOr(d, "annual_kwh", fmt(r.annual_kwh, 0, "kWh/año")))}
        ${row("Energía autoconsumida", ncOr(d, "self_consumed_kwh", `${fmt(r.self_consumed_kwh, 0, "kWh/año")} (${fmt(i.self_consumption_pct, 0)}%)`))}
        ${row("Excedente (sin valorizar salvo tarifa)", ncOr(d, "surplus_kwh", fmt(r.surplus_kwh, 0, "kWh/año")))}
        ${row("Inversión inicial", ncOr(d, "capex_usd", money(r.capex_usd)))}
        ${row("Ahorro bruto estimado", ncOr(d, "gross_savings_usd_year", money(r.gross_savings_usd_year, 2) + "/año"))}
        ${row("Mantenimiento", i.om_usd_year == null ? "no declarado (0)" : money(r.om_usd_year, 2) + "/año")}
        ${row("Ahorro neto estimado", ncOr(d, "net_savings_usd_year", money(r.net_savings_usd_year, 2) + "/año"))}
        ${row("<strong>Recuperación simple</strong>", `<strong>${payback}</strong>`)}
      </table>
      ${reasons ? `<div class="small"><strong>No calculable porque:</strong><ul>${reasons}</ul></div>` : ""}
      <div class="small muted">
        ${d.warnings.length ? `<ul>${d.warnings.map((w) => `<li>${w}</li>`).join("")}</ul>` : ""}
        <p>${d.disclaimer}</p>
        <details><summary>Fórmula y limitaciones</summary>
          <p><strong>Fórmula:</strong> ${fmt(i.system_kwp, 1)} kWp × ${fmt(d.solar_kwh_kwp_year, 0)} kWh/kWp/año; ahorro = energía autoconsumida × valor de la energía − mantenimiento; recuperación = inversión ÷ ahorro neto (solo si es positivo).</p>
          <ul>${d.limitations.map((l) => `<li>${l}</li>`).join("")}</ul>
        </details>
      </div>`;
  }

  async function loadScenarioDefaults() {
    const f = $("sim-form").elements;
    try {
      const sc = await getJSON("/api/scenario");
      for (const k of SIM_FIELDS) if (sc[k] && sc[k].value != null) f[k].value = sc[k].value;
    } catch (e) {
      f.system_kwp.value = 1; f.self_consumption_pct.value = 100; // mínimo neutro; costos quedan vacíos => No calculable
      console.warn("Escenario por defecto no disponible:", e.message);
    }
  }
  $("sim-form").addEventListener("input", () => scheduleSimulation());
  $("sim-form").addEventListener("submit", (e) => e.preventDefault());

  // ---------- Asistente ----------
  async function ask(question) {
    const out = $("answer"), btn = $("ask-btn");
    question = question.trim();
    if (!question) { out.innerHTML = '<p class="warning">Escribí una pregunta.</p>'; return; }
    const ws = Number($("w-solar").value), ww = Number($("w-wind").value);
    if (ws + ww === 0) { out.innerHTML = '<p class="warning">Subí al menos un deslizador de prioridad para consultar el ranking.</p>'; return; }
    const sim = state.selectedId ? readScenario() : {};
    btn.disabled = true;
    out.innerHTML = '<p class="muted">Pensando con los datos del mapa…</p>';
    try {
      const res = await fetch("/api/assistant", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question, selected_cell_id: state.selectedId,
          weights: { solar: ws / 100, wind: ww / 100 },
          scenario: sim.scenario || null,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      const badge = d.mode === "llm"
        ? '<span class="mode llm">Redactado con IA a partir de los datos</span>'
        : `<span class="mode deterministic" title="${d.llm_fallback_reason || ""}">Respuesta determinista (sin IA)</span>`;
      const div = document.createElement("div");
      div.className = "answer";
      div.textContent = d.answer; // texto plano: evita inyectar HTML
      out.innerHTML = badge;
      out.appendChild(div);
      if (d.cell_ids && d.cell_ids[0] && !state.selectedId) select(d.cell_ids[0], true);
    } catch (e) {
      out.innerHTML = `<p class="warning">El asistente no respondió (${e.message}). El mapa y el simulador siguen funcionando.</p>`;
    } finally {
      btn.disabled = false;
    }
  }
  $("ask-form").addEventListener("submit", (e) => { e.preventDefault(); ask($("question").value); });
  $("suggest").querySelectorAll("button").forEach((b) =>
    b.addEventListener("click", () => { $("question").value = b.textContent; ask(b.textContent); }));

  // ---------- Carga ----------
  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${url} respondió HTTP ${res.status}`);
    return res.json();
  }

  function setBanner(meta) {
    const b = $("banner");
    if (meta.synthetic) {
      b.textContent = "DATOS SINTÉTICOS DE DEMOSTRACIÓN — no son mediciones";
      b.className = "banner synthetic";
    } else {
      b.textContent = "Estimaciones preliminares · Fuente: NASA POWER / Open-Meteo · Contorno: IGN";
      b.className = "banner";
    }
    $("sources").textContent = `Dataset: ${meta.dataset} (${state.cells.length} celdas). ${sourceLine()}.`;
  }

  async function init() {
    const status = $("map-status");
    try {
      const [cells, boundary] = await Promise.all([
        getJSON("/api/cells"),
        getJSON("/api/boundary").catch(() => null), // el contorno es opcional para operar
      ]);
      state.meta = cells.metadata || {};
      state.cells = cells.features.map((f) => f.properties);
      state.byId = new Map(state.cells.map((p) => [p.id, p]));
      if (!state.cells.length) throw new Error("el dataset no tiene celdas");

      const grid = L.geoJSON(cells, {
        style: (f) => styleFor(f.properties.id),
        onEachFeature: (f, lyr) => {
          const id = f.properties.id;
          state.layersById.set(id, lyr);
          lyr.bindTooltip(() => `<strong>${coordLabel(f.properties)}</strong><br>${LAYER_NAMES[state.layer]}: ${fmt(valueOf(id))}`, { sticky: true });
          lyr.on("click", () => select(id, false));
        },
      }).addTo(map);

      let fitTo = grid.getBounds();
      if (boundary) {
        const outline = L.geoJSON(boundary, { style: { color: "#222", weight: 2, fill: false }, interactive: false }).addTo(map);
        fitTo = outline.getBounds();
        map.attributionControl.addAttribution("Contorno: IGN Argentina");
      } else {
        status.textContent = "Contorno provincial no disponible; se muestran solo las celdas.";
      }
      map.attributionControl.addAttribution(state.meta.synthetic ? "Datos sintéticos" : "NASA POWER · Open-Meteo");
      // Reserva espacio abajo para la leyenda, así no tapa celdas al abrir.
      map.fitBounds(fitTo, { paddingTopLeft: [10, 10], paddingBottomRight: [10, 110] });

      setBanner(state.meta);
      renderLegend();
      recompute();
      if (boundary) status.hidden = true;
    } catch (err) {
      status.textContent = `No se pudieron cargar los datos: ${err.message}. ¿Está corriendo el servidor?`;
      status.className = "map-status error";
      $("banner").textContent = "Error al cargar datos";
      $("banner").className = "banner error";
      console.error(err);
    }
  }

  // ---------- Controles ----------
  document.querySelectorAll('input[name="layer"]').forEach((r) =>
    r.addEventListener("change", (e) => {
      state.layer = e.target.value;
      renderLegend();
      restyleAll();
    }));
  ["w-solar", "w-wind"].forEach((id) => $(id).addEventListener("input", recompute));
  window.addEventListener("resize", () => map.invalidateSize());

  loadScenarioDefaults(); // independiente del mapa: si falla, el mapa sigue
  init();
})();
