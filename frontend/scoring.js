// Réplica EXACTA de backend/app/scoring.py (referencia matemática). Funciones puras, sin red.
// score = (wSolar·sSolar + wWind·sWind) / (wSolar + wWind), con s* ya normalizados 0-100 en el dataset.
(function (global) {
  "use strict";

  /** Pesos crudos (0-100) -> {solar, wind} que suman 1, o null si ambos son 0. */
  function normalizeWeights(solar, wind) {
    const total = solar + wind;
    if (!(total > 0)) return null;
    return { solar: solar / total, wind: wind / total };
  }

  /** Devuelve {score: 0-100 | null, partial: bool}. Ignora componentes faltantes (null). */
  function combinedScore(sSolar, sWind, w) {
    if (!w) return { score: null, partial: false };
    const parts = [[w.solar, sSolar], [w.wind, sWind]];
    const used = parts.filter(([wi, si]) => si != null && wi > 0);
    if (used.length === 0) return { score: null, partial: false };
    const totalW = used.reduce((a, [wi]) => a + wi, 0);
    const score = used.reduce((a, [wi, si]) => a + wi * si, 0) / totalW;
    const partial = parts.some(([wi, si]) => si == null && wi > 0);
    return { score: Math.round(score * 10) / 10, partial };
  }

  /** Ranking descendente; celdas sin puntaje al final; empate por id (igual que Python). */
  function rankCells(propsList, w) {
    const rows = propsList.map((p) => {
      const r = combinedScore(p.s_solar, p.s_wind, w);
      return { id: p.id, solar_index: p.s_solar ?? null, wind_index: p.s_wind ?? null, score: r.score, partial: r.partial };
    });
    rows.sort((a, b) => {
      if ((a.score == null) !== (b.score == null)) return a.score == null ? 1 : -1;
      if (a.score !== b.score) return (b.score ?? 0) - (a.score ?? 0);
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
    });
    return rows;
  }

  /** Heurística comparativa (spec §8, D3). Igual que scoring.recommendation en Python. */
  const RECOMMENDATION_MARGIN = 15;
  function recommendation(sSolar, sWind) {
    if (sSolar == null || sWind == null) return null;
    if (sSolar >= sWind + RECOMMENDATION_MARGIN) return "solar";
    if (sWind >= sSolar + RECOMMENDATION_MARGIN) return "eolica";
    return "mixta";
  }

  const api = { normalizeWeights, combinedScore, rankCells, recommendation };
  if (typeof module !== "undefined" && module.exports) module.exports = api; // node (verificación)
  global.IntiScoring = api;
})(typeof window !== "undefined" ? window : globalThis);
