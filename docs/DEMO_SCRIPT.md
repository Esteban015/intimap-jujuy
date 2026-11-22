# Guion de demo — IntiMap Jujuy (2:30 min)

> **Regla de oro:** mostrar solo lo implementado y decir «estimación preliminar» cada vez que aparezca un número. No prometer factibilidad, producción garantizada ni rentabilidad.

## Preparación (antes de subir al escenario)
1. `python -m uvicorn backend.app.main:app --port 8000` y abrir http://localhost:8000 a pantalla completa, en escritorio con al menos 1.280 px de ancho.
2. Comprobar que el cartel superior dice «Estimaciones preliminares · Fuente: NASA POWER / Open-Meteo · Contorno: IGN». Si dice «DATOS SINTÉTICOS», reiniciar el servidor **sin** `INTIMAP_DATASET=sample`.
3. Dejar los sliders en Solar 67% y Eólico 33%, capa «Puntaje combinado» y ninguna celda seleccionada (recargar la página).
4. Mapa base OSM **apagado**: no depende de internet.
5. Tener abiertas en otra pestaña las capturas de `docs/screenshots/` como último plan B.

## Guion

| # | Tiempo | En pantalla | Qué decir |
|---|---|---|---|
| 1. Problema | 0:00–0:20 | Mapa completo con puntaje combinado | «Decidir dónde instalar energía renovable en Jujuy hoy implica cruzar datos dispersos y técnicos: irradiación, viento, altitud. Y la provincia es muy diversa: Puna a más de 3.500 metros, quebradas y Yungas.» |
| 2. Solución | 0:20–0:35 | Señalar el cartel de fuentes y la leyenda | «IntiMap divide Jujuy en 104 zonas de unos 28 km con datos climatológicos de 25 años de NASA POWER, altitud de Open-Meteo y el contorno oficial del IGN. Todo corre localmente, sin internet.» |
| 3. Mapa | 0:35–0:55 | Cambiar a «Potencial solar relativo», después a «Recurso eólico relativo» y volver a «Puntaje combinado» | «En solar destaca la Puna oeste. En viento, el máximo está en el suroeste de la Puna. Estos índices de 0 a 100 son relativos dentro de Jujuy: comparan zonas, no certifican viabilidad.» |
| 4. Prioridades | 0:55–1:15 | Bajar Solar a 0 y subir Eólico a 100: cambian los colores y el ranking. Volver a 60/30. | «Si mi prioridad es el viento, el ranking se recalcula al instante en el navegador, sin pedir nada al servidor.» |
| 5. Ficha | 1:15–1:35 | Clic en el n.º 1 del ranking, la celda del oeste de la Puna | «Esta zona tiene 7,37 kWh por m² por día y unos 2.164 kWh por kWp al año, estimados. Fíjense en la densidad del aire: 0,81, un tercio menos que al nivel del mar. Por eso el mismo viento rinde menos en altura. Cada dato dice si fue descargado o calculado.» |
| 6. Simulación | 1:35–1:55 | Bajar al simulador y cambiar la potencia de 5 a 10 kWp | «Con un escenario hipotético que el usuario edita (900 dólares por kWp, 10 centavos por kWh, 80% de autoconsumo), la recuperación simple da unos 5 años. Si falta un dato dice "No calculable"; no inventa.» |
| 7. Asistente | 1:55–2:15 | Botón «¿Dónde conviene instalar solar para una comunidad de 50 familias?» | «El asistente responde con los números del mapa. Y no dice que alcanza: dice que falta el consumo de la comunidad y explica cómo dimensionarlo. Funciona sin IA; si hay una clave, la IA solo redacta y se descarta si cambia un número.» |
| 8. Cierre | 2:15–2:30 | Volver al mapa completo | «IntiMap es un primer filtro transparente para municipios, comunidades e instaladores: qué zonas conviene estudiar primero. El paso siguiente es sumar red eléctrica, localidades y validación con especialistas.» |

> El cierre comercial (informes para empresas y derivación a instaladores) es una **hipótesis** de modelo de negocio (ver `ROADMAP.md`). Presentarlo como posibilidad, no como tracción.

## Frases a evitar
- ❌ «Esta zona es viable» o «garantiza X años de retorno». ✅ «Estimación preliminar con un escenario editable.»
- ❌ «Produciría X kWh de energía eólica». ✅ «Tiene un índice de recurso eólico alto en comparación con el resto de Jujuy.»
- ❌ «Datos medidos en Jujuy». ✅ «Climatología satelital y de reanálisis de NASA POWER.»

## Plan de contingencia
| Falla | Qué hacer |
|---|---|
| **No hay internet** | No afecta: datos, Leaflet y asistente son locales. No activar el mapa base OSM. |
| **El LLM no responde o no hay clave** | No afecta: el asistente responde en modo determinista y la UI lo indica («Respuesta determinista (sin IA)»). Decirlo como fortaleza. |
| **El servidor no arranca** | Revisar que el venv esté activo y `pip install -r backend/requirements.txt`. Mientras tanto, mostrar las capturas de `docs/screenshots/`. |
| **El puerto 8000 está ocupado** | `python -m uvicorn backend.app.main:app --port 8010` y abrir ese puerto. |
| **Aparece «DATOS SINTÉTICOS»** | Falta `data/processed/cells.geojson` o se forzó el modo sample. Reiniciar sin `INTIMAP_DATASET` o explicar que es el modo de respaldo. |
| **La pantalla es chica o el proyector tiene poca resolución** | Achicar el zoom del navegador al 80–90%. En pantallas angostas los paneles se apilan y hay que bajar con scroll. |

## Preguntas probables del jurado
- **«¿Qué tan precisos son los datos?»** Son climatología de 25 años de NASA POWER con resolución de 0,5° a 1°: celdas vecinas pueden compartir valores. Sirven para comparar zonas, no para diseñar una planta.
- **«¿Por qué no calculan energía eólica?»** Haría falta un modelo de turbina y la distribución de vientos. Mostramos un índice comparativo y lo decimos explícitamente.
- **«¿Usan IA para los cálculos?»** No. Todos los cálculos son deterministas en Python; la IA, si se activa, solo redacta y se valida.
- **«¿Pueden usarlo comercialmente?»** Habría que reemplazar la fuente de altitud (Open-Meteo es no comercial) y confirmar la licencia del IGN.
