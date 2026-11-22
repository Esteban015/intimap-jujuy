# Decisiones técnicas — Fase 0

1. **Spec original no disponible en el repo.** Se trabajó con el resumen del «Informe comparativo» (Proyecto A). Si aparece el documento «Contexto para Cursor: Mapa de potencial renovable de Jujuy», revisar contratos antes de la Fase 1.
2. **Un solo proceso:** FastAPI sirve la API y el frontend estático. Sin microservicios, sin auth, sin base de datos (GeoJSON local).
3. **Qué necesita FastAPI de verdad:**
   - Imprescindible: el proxy LLM opcional (para que la clave no llegue al navegador).
   - Conveniente: el puntaje y la simulación en Python como única fuente de verdad (se pueden probar con funciones puras, sin duplicar en JS) y servir los archivos estáticos.
   - Estático: grilla, irradiación, viento y supuestos son archivos precalculados en `data/`.
4. **Datos offline:** la app no llama a NASA POWER ni a Open-Meteo en ejecución. Los scripts de la Fase 1 generan `data/processed/cells.geojson`. Mientras no exista, se usa `data/sample/` (6 celdas **sintéticas**), y `/api/health` y la UI lo advierten.
5. **Calidad por campo** (`real` / `aproximado` / `sintetico`) en cada celda. Un faltante es `null`, nunca 0.
6. **Puntaje = índice relativo min-max dentro de Jujuy (0-100).** Se presenta como comparación entre zonas, no como viabilidad.
7. **Eólico solo como índice de recurso** (velocidad a 50 m). No se calculan kWh eólicos porque no hay modelo de turbina ni distribución de Weibull.
8. **Simulación solar simple** (kWp × GHI × 365 × PR) con supuestos visibles y una lista explícita de lo omitido. Costo y tarifa quedan `null` hasta tener fuente.
9. **Asistente:** la plantilla determinística es el camino por defecto. El LLM es opcional, solo redacta a partir de `facts_used` y nunca calcula.
10. **Endpoints de Fases 2-3 como stubs 501** que ya validan la entrada (422) y la existencia de la celda (404), para que frontend y backend trabajen contra el contrato desde ahora.
11. **Leaflet (Fase 2):** copiarlo dentro de `frontend/vendor/` en vez de usar un CDN. Las teselas de fondo son opcionales: la grilla debe verse aunque no haya internet.
12. **Rutas:** se usan `/api/cells` y `/api/cells/{id}`. El plan de Planner Express proponía `/api/grid` y `/api/cell/{id}`; se unificó en los nombres del contrato C2.

# Decisiones — Fase 1 (datos)

13. **Fuente de requisitos:** ahora es `docs/PROJECT_SPEC.md`. Se mantiene FastAPI + frontend estático en lugar del Next.js del spec, por indicación expresa.
14. **Rutas de datos:** el spec pide `data/cells.geojson` y `data/jujuy.geojson`, pero el enunciado de la Fase 1 pide `data/processed/`. Se usa `data/processed/`, que es la instrucción más reciente. `cells_raw.json` se reemplaza por la caché por celda en `data/raw/`.
15. **Fórmulas:** se adoptan las del spec §8 (PR 0,80 + factor de temperatura, ρ por altitud, WPD = 0,5·ρ·v³, min-max 0-100) en `backend/app/indicators.py`, como única fuente que reutilizará `scoring.py`. Esto reemplaza el PR 0,75 del contrato de la Fase 0. No se calculó economía en esta fase.
16. **Puntaje en el cliente (spec §9) contra `/api/scores` (Fase 0):** se resolverá en la Fase 2. Propuesta conservadora: replicar en JS las fórmulas de `indicators.py` (los sliders responden al instante) y dejar `/api/scores` como verificación.
17. **Asistente:** el spec define `POST /api/assistant`. En la Fase 3 se adopta ese nombre y `/api/explain` deja de usarse.
18. **Economía:** el spec usa USD de ejemplo (900 USD/kWp y 0,10 USD/kWh) etiquetados como ejemplo; la Fase 0 dejó ARS en `null`. Lo decide P3 (dueña de `data/assumptions.json`), que no se tocó.
19. **Contorno:** se usa el IGN, que es oficial. El de geoBoundaries (Wikimedia, 2006) queda como respaldo con etiqueta "NO oficial". No hay contorno fabricado: si ninguna fuente responde, el script falla.
20. **Grilla:** celdas cuadradas de 0,25° alineadas a múltiplos de 0,25°, recortadas al contorno; se conservan todas las intersecciones, incluso las astillas del borde. El ID es el centro de la celda completa, así que no cambia si se recorta distinto. Las APIs se consultan en un punto **interior** del recorte (`query_point`).
21. **Viento a 50 m:** la climatología de NASA POWER ofrece WS50M. No se extrapola a 100 m porque requeriría suponer una rugosidad.
22. **Faltantes:** si una API falla, el campo queda en `null` con `quality=faltante`. Nunca se rellena con valores sintéticos. `make_synthetic.py` no se creó: el respaldo sintético son las 6 celdas de `data/sample/`.
23. **Caché en git:** `data/raw/` deja de estar ignorado. Son menos de 1 MB, no tiene secretos y permite reconstruir el dataset sin red (`fetch_data.py --offline`).
24. **Vocabulario de calidad:** `real` / `estimado` / `faltante` / `sintetico`. `aproximado` se reemplaza por `estimado`.

# Decisiones — Fase 2 (mapa)

25. **Puntaje: Python es la referencia y el navegador recalcula** (resuelve la decisión 16). `backend/app/scoring.py` define `score = (w_s·s_solar + w_w·s_wind)/(w_s + w_w)`. `frontend/scoring.js` es una réplica pura con el mismo redondeo (half-up a 1 decimal), el mismo tratamiento de nulos y el mismo desempate por id. Los sliders no hacen requests. `POST /api/scores` usa `scoring.py` y sirve para verificar la equivalencia: con 5 combinaciones de pesos, la diferencia máxima fue 0,000 y el orden de las 104 celdas fue idéntico. La normalización climática NO se repite en el frontend, porque usa `s_solar` y `s_wind` del GeoJSON.
26. **Pesos:** solo solar y eólico. Red y caminos quedan deshabilitados porque no hay datos reales (spec §8: peso 0 si no existen). Los valores por defecto son 60/30, el spec sin el 0,1 de red, renormalizados a 67%/33%. Con ambos pesos en 0, el puntaje combinado es `null`, las celdas se ven grises, el ranking se oculta, aparece un aviso y `/api/scores` responde 422.
27. **Leaflet 1.9.4 local** en `frontend/vendor/leaflet/` (licencia BSD-2, incluida). Sin CDN. El mapa base de OSM es opcional, está apagado por defecto y requiere internet; las celdas y el contorno se ven sin conexión.
28. **Escala de color:** RdYlGn de 5 clases (spec §11: rojo-amarillo-verde) con números en la leyenda. El rojo-verde es difícil de distinguir para personas daltónicas; se mitiga con las etiquetas numéricas y la ficha.
29. **Muestra sintética:** como no tiene temperatura ni altitud, `data_loader` normaliza sus índices directamente desde GHI y viento y marca todos los campos como `sintetico`. La UI muestra un cartel rojo.
30. **Ficha:** separa "Datos descargados" (`real`) de "Indicadores calculados" (`estimado`). No muestra payback (Fase 3) ni la recomendación solar/eólica/mixta del spec §8. Esa recomendación también queda para la Fase 3, porque depende de que el equipo valide el umbral de 15.

# Decisiones — Fase 3 (simulador y asistente)

31. **D1, economía en USD editable.** El escenario por defecto está en `data/economic_scenario.json` (900 USD/kWp, 0,10 USD/kWh, 5 kWp, 80% de autoconsumo) y se rotula siempre "ESCENARIO HIPOTÉTICO EDITABLE". Costo y tarifa son ejemplos del spec, no cotizaciones. `data/assumptions.json` (de P3: ARS y PR 0,75) **no se modificó** porque es de otro integrante; queda obsoleto y P3 debe retirarlo o alinearlo.
32. **Una sola implementación del cálculo económico:** `backend/app/finance.py`. El navegador llama a `/api/simulate` con un debounce de 250 ms, a diferencia del puntaje, que no lo necesita al instante. El asistente usa la misma función.
33. **Reglas de cálculo:**
    - Si falta un dato, el resultado es `null` con su motivo y la UI muestra «No calculable».
    - El excedente vale 0 salvo que se informe una tarifa de inyección.
    - Si el mantenimiento no se declara, se toma 0 con advertencia.
    - Sin recuperación si el ahorro neto es menor o igual a 0.
    - La recuperación es simple: no es VAN ni TIR.
    - El cálculo usa `solar_kwh_kwp_year` de la Fase 1 (PR 0,80 + temperatura).
34. **D2, el endpoint canónico es `POST /api/assistant`.** `/api/explain` y su contrato fueron retirados.
35. **D3, umbral de 15 puntos** como heurística comparativa (`scoring.recommendation` y su réplica en `scoring.js`). Se muestra en la ficha con una nota de que no certifica viabilidad.
36. **Asistente determinista por intención:** comunidad, viento, economía, explicar la celda o ranking, detectada por palabras clave.
    - Si hay celda seleccionada, "¿por qué esta zona?" explica esa celda.
    - Para la pregunta de "50 familias" no afirma que alcance: dice que falta el consumo y da kWh por kWp para dimensionar.
    - No inventa localidades, red, costos ni kWh eólicos.
    - Máximo 150 palabras; si se pasa, recorta el "Por qué" y nunca la advertencia.
37. **LLM opcional con el SDK oficial `anthropic`:**
    - Se activa solo si existe `LLM_API_KEY` en el backend. El modelo por defecto es `claude-opus-5-5` (cambiable con `LLM_MODEL`), con effort `low`, fallback del servidor ante rechazos, timeout de 15 s y sin reintentos.
    - Solo reescribe el borrador. Se descarta si introduce números que no están en el borrador, pasa de 150 palabras, pierde secciones, falla, tarda o termina con un `stop_reason` distinto de `end_turn`.
    - La clave nunca llega al frontend.
    - **No se probó contra la API real** (no hay clave). Solo se probaron los caminos de descarte (sin clave y sin conexión).

# Decisiones — Fase 4 (documentación)

38. **`data/assumptions.json` se conserva sin modificar como archivo histórico.** Ningún componente lo lee (verificado con grep en `backend/`, `frontend/` y `scripts/`) y no hay pruebas que dependan de él. Sus valores (PR 0,75, ARS, costo y tarifa en `null`) están desactualizados y contradicen `economic_scenario.json`, que es la fuente vigente. Pertenece a P3 según `TEAM.md`; retirarlo queda a su criterio. Análisis completo en `DATA_METHODOLOGY.md` §8.
39. **README del producto.** El README anterior, que describía el kit Colmena, se preservó como `docs/COLMENA_KIT.md`, con un encabezado que aclara que es histórico.
40. **Pruebas:** el repositorio no incluye tests automatizados; las validaciones de las Fases 0 a 4 se hicieron con scripts de smoke externos. Incorporarlos quedó en `ROADMAP.md` §2. En la Fase 4 no se cambió código.
