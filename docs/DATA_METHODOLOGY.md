# Metodología de datos — IntiMap Jujuy

Este documento explica de dónde salen los números que muestra IntiMap y qué significan. Cada afirmación se verificó contra el código (`scripts/`, `backend/app/`) y contra los datos versionados (`data/processed/cells.geojson` y `data/raw/`).

> **Alcance:** IntiMap produce **indicadores de prefactibilidad para comparar zonas**. No reemplaza mediciones in situ, estudios de recurso ni estudios de ingeniería.

## 1. Tipos de dato

Cada valor de cada celda lleva una etiqueta de calidad en `properties.quality`, que la interfaz muestra.

| Tipo | Etiqueta | Ejemplos en IntiMap | Cómo se obtiene |
|---|---|---|---|
| **Observado o modelado por la fuente** | `real`, que la UI muestra como «descargado» | Irradiación GHI, temperatura media, viento a 50 m y altitud | Descargado tal cual de NASA POWER u Open-Meteo. Ojo: NASA POWER combina modelos y reanálisis (MERRA-2) con satélite (CERES SYN1deg); no son mediciones de estaciones locales. |
| **Derivado por fórmula** | `estimado`, que la UI muestra como «calculado» | kWh/kWp/año, densidad del aire, índice eólico en W/m² e índices de 0 a 100 | Fórmulas de la §5 aplicadas a los datos descargados. |
| **Faltante** | `faltante` | Ninguno en el dataset actual: 104 de 104 celdas completas | La fuente no respondió. El valor es `null` y nunca se rellena. |
| **Sintético** | `sintetico` | Solo `data/sample/` (6 celdas) | Inventado para desarrollo. La UI muestra un cartel rojo. |
| **Escenario hipotético** | «Escenario hipotético editable» | Costo por kWp, valor de la energía, autoconsumo y potencia por defecto | Valores de ejemplo del spec, editables por el usuario. **No son cotizaciones ni tarifas oficiales.** |

## 2. Geometrías

- **Contorno:** Instituto Geográfico Nacional (IGN), WFS oficial, capa `ign:provincia` filtrada por `nam='Jujuy'`, en EPSG:4326. Se descargó el 2026-11-22 y la respuesta original está en `data/raw/boundary_ign_wfs.json`.
  - El script tiene un respaldo, geoBoundaries ARG ADM1 (origen Wikimedia, año 2006), marcado como NO oficial. **No se usó.**
  - El área aproximada del contorno es 53.491 km², coherente con la superficie conocida de la provincia.
- **Contorno para dibujar:** simplificado con una tolerancia de 0,002° (~200 m), en `data/processed/jujuy.geojson`. Los cálculos de grilla usan el contorno **sin simplificar**.
- **Grilla:**
  - Celdas cuadradas de 0,25° (unos 28 km en sentido norte-sur), alineadas a múltiplos de 0,25° e intersectadas con el contorno.
  - Resultan **104 celdas**, de las cuales 58 son de borde (recortadas) y 7 cubren menos del 5% de una celda completa. Se conservan todas para no dejar huecos.
  - La unión de las celdas cubre la provincia completa: la relación de áreas es 1,000000.
- **Identificador estable:** `c_<lat>_<lon>` del centro de la celda *completa*. No cambia aunque se recorte distinto.
- **Punto de consulta (`query_point`):** el centroide del recorte, o un punto interior si el centroide cae fuera. Siempre está dentro de Jujuy.
- **Área:** aproximada, con la fórmula `grados² × 111,32² × cos(latitud del centroide)`.

## 3. Fuentes climáticas y de altitud

| Variable | Campo | Fuente / parámetro | Unidad | Período | Resolución nativa |
|---|---|---|---|---|---|
| Irradiación global horizontal | `solar_ghi_kwh_m2_day` | NASA POWER `ALLSKY_SFC_SW_DWN`, media anual (`ANN`) | kWh/m²/día | Ene-2001 a dic-2025 (climatología de 25 años) | ~1° × 1° |
| Temperatura media a 2 m | `temp_mean_c` | NASA POWER `T2M`, `ANN` | °C | Ídem | ~0,5° × 0,625° (MERRA-2) |
| Viento medio a 50 m | `wind_speed_50m_ms` | NASA POWER `WS50M`, `ANN` | m/s | Ídem | ~0,5° × 0,625° |
| Altitud | `elevation_m` | Open-Meteo Elevation API (Copernicus DEM GLO-90) | m s.n.m. | Estática | 90 m, **en un punto** |

- **NASA POWER:** Climatology API v2.10.2, comunidad RE, un punto por celda. Fuentes declaradas en la respuesta: MERRA2, SYN1DEG y POWER. Descarga del 2026-11-22 entre las 14:54 y las 14:59 UTC.
  - El script verifica que las unidades devueltas sean exactamente `kW-hr/m^2/day`, `C` y `m/s`; si no coinciden, descarta el valor.
  - El valor de relleno (`-999`) se convierte en `null`.
- **Open-Meteo:** una consulta por lote de hasta 100 coordenadas, descargada el 2026-11-22. Es gratuita **solo para uso no comercial**.
- **Por qué climatología y no pronóstico:** la prefactibilidad requiere promedios de largo plazo, no el clima de un día.

### Consecuencia de la resolución
La grilla de 0,25° es **más fina** que los datos de NASA POWER. En el dataset hay solo **12 valores distintos de GHI** y **25 de viento y temperatura** para 104 celdas, así que celdas vecinas comparten valores. Las diferencias dentro de un mismo bloque vienen de la altitud, que se mide por punto y modifica la densidad del aire, y de la temperatura. **No hay que interpretar diferencias finas entre celdas vecinas.**

### Rangos observados en el dataset (104 celdas)
| Variable | Mínimo | Máximo |
|---|---|---|
| GHI (kWh/m²/día) | 4,76 | 7,37 |
| Temperatura media (°C) | 2,6 | 23,6 |
| Viento a 50 m (m/s) | 3,29 | 7,87 |
| Altitud (m) | 334 | 5.258 |
| Densidad del aire (kg/m³) | 0,716 | 1,186 |
| Generación específica (kWh/kWp/año) | 1.286 | 2.170 |
| Índice eólico (W/m²) | 13,6 | 201,8 |

## 4. Procedencia por celda
Cada celda conserva:
- **Fuente y fecha de descarga:** `provenance.nasa_power.fetched_at` y `provenance.open_meteo_elevation.fetched_at`.
- **Período:** `provenance.nasa_power.period`.
- **Altura del viento:** `wind_height_m = 50`.
- **Calidad por campo:** `quality`.

A nivel del dataset, `metadata.variables` documenta unidades, fórmulas y descripciones, y `metadata.sources` las fuentes y sus condiciones de uso.

## 5. Fórmulas
Las fórmulas físicas están en `backend/app/indicators.py`, el puntaje en `backend/app/scoring.py` y su réplica en `frontend/scoring.js`. Las constantes vienen del spec del proyecto (§8).

### 5.1 Potencial solar (estimado)
```
Tcell        = Tamb + 20                       [°C]
temp_factor  = 1 − 0,004 × (Tcell − 25)
kWh/kWp/año  = GHI × 365 × 0,80 × temp_factor
```
- 0,80 es un *performance ratio* base que agrupa pérdidas de inversor, cableado, suciedad y otras. Es una aproximación.
- Usa **irradiación sobre plano horizontal**. Un panel inclinado hacia el norte, a la latitud de Jujuy (−22° a −25°), suele recibir algo más de energía anual, así que este supuesto tiende a **subestimar**.
- Usa la **temperatura media anual de 24 horas**, que incluye la noche. Durante las horas de producción la celda está más caliente, así que el factor de temperatura tiende a **sobreestimar**. En la Puna fría (Tamb ≈ 3 °C) el factor queda apenas por encima de 1.
- Los dos sesgos tienen signo opuesto y no se cuantificaron. Por eso el resultado es un orden de magnitud comparativo, no un pronóstico de producción.

### 5.2 Densidad del aire (estimado)
```
ρ = 1,225 × (1 − 2,25577e-5 × altitud_m)^4,25588     [kg/m³]
```
Usa la atmósfera estándar. A 4.100 m, ρ ≈ 0,81 kg/m³, un 34% menos que al nivel del mar. Por eso el mismo viento entrega menos potencia en la Puna.

### 5.3 Índice de recurso eólico (estimado, comparativo)
```
WPD_índice = 0,5 × ρ × v̄³      [W/m²]   con v̄ = velocidad media anual a 50 m
```
> **Este índice NO es la generación anual de un aerogenerador.**
> - Usa la velocidad *media*. La densidad de potencia real depende del promedio de v³, que es mayor que el cubo de la media (con una distribución de Rayleigh, cerca de 1,9 veces). Por eso el índice **subestima** el valor absoluto. Sirve para *comparar* celdas entre sí.
> - Calcular energía anual requeriría la curva de potencia de una turbina, la distribución de vientos (Weibull), la altura de buje, la rugosidad y las pérdidas. IntiMap **no calcula kWh eólicos**.

### 5.4 Normalización (índices relativos de 0 a 100)
```
s = 100 × (x − mín) / (máx − mín)       sobre las celdas con dato
```
- `s_solar` normaliza `solar_kwh_kwp_year` y `s_wind` normaliza `wind_power_density_w_m2`.
- Un **100 significa "la mejor celda de Jujuy en esta variable"**, no «viable».
- Si se agregan o quitan celdas, los índices cambian.
- En la muestra sintética, los índices se normalizan directamente desde GHI y viento, porque no tiene temperatura ni altitud.

### 5.5 Ponderación y puntaje combinado
```
w_solar, w_eólico ∈ [0, 1], renormalizados para sumar 1
score = (w_solar × s_solar + w_eólico × s_eólico) / (w_solar + w_eólico)
```
- Los valores por defecto de la UI son 60/30, que renormalizados dan **67% / 33%**. Es el spec sin el peso de red eléctrica, que está deshabilitado por falta de datos.
- Con ambos pesos en 0, el puntaje no se calcula: la UI lo avisa y la API responde 422.
- El redondeo es half-up a un decimal, idéntico en Python y en JS (verificado).

### 5.6 Recomendación preliminar (heurística)
```
solar  si s_solar ≥ s_eólico + 15
eólica si s_eólico ≥ s_solar + 15
mixta  en otro caso
```
Es una **heurística comparativa** del spec: compara índices relativos y no evalúa viabilidad. En el dataset actual: 74 celdas «solar», 18 «mixta» y 12 «eólica».

## 6. Modelo de estimación económica (solo solar)
Está implementado en `backend/app/finance.py`, con una sola implementación que usan la API y el asistente.

```
generación_anual  = kWp × kWh/kWp/año (de la celda)            [kWh/año]
inversión         = kWp × costo_por_kWp                        [USD]
autoconsumo       = generación_anual × %autoconsumo / 100       [kWh/año]
excedente         = generación_anual − autoconsumo              [kWh/año]
ahorro_bruto      = autoconsumo × valor_energía
                    (+ excedente × tarifa_inyección, solo si el usuario la informa)   [USD/año]
ahorro_neto       = ahorro_bruto − mantenimiento_anual          [USD/año]
recuperación      = inversión ÷ ahorro_neto   (solo si ahorro_neto > 0)   [años]
```

**Reglas:**
- Si falta el costo o el valor de la energía, el resultado dice «No calculable» y da el motivo. No se inventan valores.
- El excedente no tiene valor por defecto.
- Si el mantenimiento no se declara, se toma 0 con una advertencia explícita, porque sobreestima el ahorro.
- Si el ahorro neto es menor o igual a 0, no hay recuperación.
- Validaciones de entrada: potencia mayor a 0, costos y tarifas no negativos, autoconsumo entre 0 y 100%.

**Escenario por defecto** (`data/economic_scenario.json`, **hipotético y editable**): 5 kWp, 900 USD/kWp, 0,10 USD/kWh y 80% de autoconsumo. Costo y tarifa son los «valores de ejemplo» del spec. **No son cotizaciones de mercado ni tarifas oficiales de la distribuidora.**

**Ejemplo verificable** (celda `c_-23.375_-67.125`, con 2.164 kWh/kWp/año):

| Paso | Cálculo | Resultado |
|---|---|---|
| Generación | 5 × 2.164 | 10.820 kWh/año |
| Autoconsumo | 10.820 × 80% | 8.656 kWh/año |
| Ahorro bruto | 8.656 × 0,10 | 865,60 USD/año |
| Inversión | 5 × 900 | 4.500 USD |
| Recuperación simple | 4.500 ÷ 865,60 | 5,2 años |

**El modelo no incluye** VAN, TIR, tasa de descuento, inflación, financiamiento, degradación de paneles, reemplazo del inversor, baterías, costos de conexión o permisos, sombreado ni variaciones de tarifa. **La recuperación simple no es una rentabilidad garantizada.**

## 7. Supuestos y restricciones
- **Sin producción eólica en kWh**, ni ángulo de montaje, altura de paneles o aptitud estructural del terreno.
- **Sin factores de red eléctrica, caminos ni localidades:** no hay datos reales en el proyecto.
- **El asistente solo usa los datos del contexto:** dataset, ranking, celda y escenario. Si falta un dato, lo dice («sin dato»). Ante «¿alcanza para 50 familias?» responde que **falta el consumo** y explica cómo dimensionar.
- **Licencias:** Open-Meteo es solo para uso no comercial, lo que obliga a reemplazar la fuente de altitud para un uso comercial. Los términos del IGN están a confirmar.

## 8. Archivo `data/assumptions.json` (histórico)
| Pregunta | Respuesta (verificada en el código) |
|---|---|
| ¿Quién lo usa? | **Nadie.** Ningún módulo de `backend/`, `frontend/` ni `scripts/` lo lee. `main.py` lee solo `economic_scenario.json`. |
| ¿Hay pruebas que dependan de él? | No. El repositorio no tiene pruebas automatizadas. |
| ¿Sus valores siguen vigentes? | **No.** Usa PR 0,75 (vigente: 0,80 con factor de temperatura), moneda ARS (vigente: USD) y costo y tarifa en `null`. |
| ¿Contradice `economic_scenario.json`? | Sí, en moneda y en PR. Como no lo usa nada, la contradicción no afecta los resultados. |
| Decisión | **Se conserva sin modificar como archivo histórico** de la Fase 0. Pertenece a P3 según `TEAM.md`, y borrarlo no aporta nada funcional. Fuente vigente: `economic_scenario.json` (ver DECISIONS 31 y 38). Retirarlo queda a criterio de P3. |

## 9. Reproducibilidad
```bash
pip install -r scripts/requirements.txt
python scripts/build_grid.py --offline     # reconstruye contorno y grilla desde data/raw/
python scripts/fetch_data.py --offline     # reconstruye cells.geojson desde data/raw/
```
La reconstrucción offline produce un dataset con features idénticas al versionado; se verificó en las Fases 1 y 4. Sin `--offline`, los scripts descargan solo lo que falta en la caché.
