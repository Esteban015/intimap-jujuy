# Guion de demo — IntiMap Jujuy

> **Regla de oro:** mostrar solo lo implementado y decir «estimación preliminar» cada vez que aparezca un número. No prometer factibilidad, producción garantizada, rentabilidad ni precisión de predio.

## Preparación (5 minutos antes)
1. Abrir la app:
   - **Producción:** https://intimap-jujuy.onrender.com, **abierta unos minutos antes**. En el plan free tarda cerca de 1 minuto en despertar.
   - **Plan B local:** `python -m uvicorn backend.app.main:app --port 8000` → http://localhost:8000. Funciona sin internet.
2. Navegador a pantalla completa, en escritorio con al menos 1.280 px de ancho y zoom al 100% (al 90% si el proyector es chico).
3. Dejar abierta la **landing** (`/`), arriba de todo.
4. Precargar `/mapa/` en otra pestaña y comprobar:
   - Que el cartel diga «Estimaciones preliminares · Fuente: NASA POWER / Open-Meteo · Contorno: IGN». Si dice «DATOS SINTÉTICOS», reiniciar el servidor sin `INTIMAP_DATASET=sample`.
   - Que los sliders estén en Solar 67% y Eólico 33%, con la capa «Puntaje combinado» y sin celda seleccionada (recargar la página).
5. Dejar el mapa base OSM apagado.
6. Plan C: tener las capturas de `docs/screenshots/` abiertas en una pestaña.

## Cómo se lee el mapa (decirlo una vez)
Cada capa usa **una escala secuencial de un solo tono**: verde para el combinado, dorado para lo solar y azul pizarra para lo eólico. **Cuanto más oscuro el tono, mayor la puntuación relativa** dentro de Jujuy. La leyenda muestra los cortes 0/20/40/60/80/100. Las celdas con trama diagonal no tienen dato o no tienen pesos asignados.

## Recorrido principal (≈ 120 segundos)

| # | Tiempo | En pantalla | Qué decir |
|---|---|---|---|
| 1. Landing | 0:00–0:12 | Landing: hero con «El primer filtro para la energía renovable en Jujuy» | «IntiMap es el primer filtro para la energía renovable en Jujuy: una evaluación preliminar para saber qué zonas conviene estudiar primero.» |
| 2. Problema | 0:12–0:24 | Hacer scroll a «El problema» | «Hoy, decidir dónde estudiar un proyecto solar o eólico implica cruzar datos dispersos y técnicos en una provincia que va desde las Yungas hasta la Puna a más de 5.000 metros. Para municipios y comunidades, ese primer paso suele ser caro y lento.» |
| 3. Propuesta | 0:24–0:34 | Scroll a «Qué es y qué no es» | «Compara las 104 zonas con 25 años de datos públicos y es honesto: no es un estudio de factibilidad, es un filtro que orienta.» |
| 4. Acceso al mapa | 0:34–0:40 | Clic en «Explorar mapa energético» (`/mapa/`) | «Entremos a la herramienta.» |
| 5. Capas | 0:40–0:56 | Cambiar a «Potencial solar relativo» (dorado) y después a «Recurso eólico relativo» (azul) | «Cuanto más oscuro, mayor el potencial relativo. En solar destaca la Puna oeste. En viento, el máximo está en el suroeste de la Puna. Son comparaciones dentro de Jujuy, no certificaciones.» |
| 6. Prioridades | 0:56–1:10 | Volver a «Puntaje combinado». Bajar Solar a 0 y subir Eólico a 100: cambian colores y ranking. Volver a 60/30. | «Si mi prioridad es el viento, el ranking se recalcula al instante en el navegador, sin pedir nada al servidor.» |
| 7. Zona | 1:10–1:24 | Clic en el n.º 1 del Top 5. La celda queda marcada y la provincia sigue visible. | «Esta zona tiene 7,37 kWh por m² por día y unos 2.164 kWh por kWp al año, estimados. A 4.100 metros el aire es un tercio menos denso, por eso el mismo viento rinde menos. Cada dato dice si fue descargado o calculado.» |
| 8. Simulación | 1:24–1:38 | Mostrar el simulador | «Con un escenario hipotético que el usuario edita (5 kWp, 900 dólares por kWp, 10 centavos por kWh, 80% de autoconsumo), la recuperación simple da 5,2 años. Si falta un dato, dice "No calculable"; no inventa.» |
| 9. Asistente | 1:38–1:52 | Botón «¿Dónde conviene instalar solar para una comunidad de 50 familias?» | «El asistente responde con los números del mapa, y no dice que alcanza: dice que falta el consumo y explica cómo dimensionar. Funciona sin IA.» |
| 10. Cierre | 1:52–2:00 | Volver a la landing con «← Inicio» | «IntiMap ayuda a municipios, comunidades e instaladores a llegar mejor preparados a un estudio de sitio. Como hipótesis comercial, informes preliminares y derivación a instaladores locales.» |

## Versión corta (≈ 60 segundos)

| # | Tiempo | En pantalla | Qué decir |
|---|---|---|---|
| 1 | 0:00–0:10 | Landing (hero) | «IntiMap: el primer filtro para la energía renovable en Jujuy. Compara 104 zonas con datos públicos de 25 años.» |
| 2 | 0:10–0:15 | «Explorar mapa energético» | — |
| 3 | 0:15–0:28 | Capa solar y después combinada. Mover el slider Eólico. | «Cuanto más oscuro, mayor el potencial relativo. Cambio prioridades y el ranking se recalcula al instante.» |
| 4 | 0:28–0:42 | n.º 1 del Top 5 y el simulador | «Esta zona produce unos 2.164 kWh por kWp al año, estimados. Con un escenario hipotético editable, la recuperación simple da 5,2 años.» |
| 5 | 0:42–0:54 | Asistente: pregunta de las 50 familias | «Explica con números y aclara lo que falta: el consumo de la comunidad.» |
| 6 | 0:54–1:00 | — | «Es una evaluación preliminar, no un estudio de sitio. Ayuda a decidir qué estudiar primero.» |

> El cierre comercial (informes, derivación a instaladores) es una **hipótesis** sin validar (ver `ROADMAP.md`). Presentarlo como posibilidad, no como tracción.

## Frases a evitar
- ❌ «Esta zona es viable» o «garantiza X años de retorno». ✅ «Estimación preliminar con un escenario editable.»
- ❌ «En tu terreno vas a producir…». ✅ «A escala de zona, de unos 28 km.»
- ❌ «Produciría X kWh de energía eólica». ✅ «Tiene un índice de recurso eólico alto comparado con el resto de Jujuy.»
- ❌ «Datos medidos en Jujuy». ✅ «Climatología satelital y de reanálisis de NASA POWER.»
- ❌ «Ya genera impacto en comunidades». ✅ «Puede ayudar; su impacto todavía no fue medido.»

## Plan de contingencia
| Falla | Qué hacer |
|---|---|
| **Render tarda en responder (plan free)** | Esperar el aviso de carga, de cerca de 1 minuto, mientras se habla del problema. Si no responde, pasar al plan B local. |
| **No hay internet** | Usar la app local: datos, fuentes, íconos, Leaflet y asistente son locales. No activar el mapa base OSM. |
| **El LLM no responde o no hay clave** | No afecta: el asistente responde en modo determinista y la UI lo indica («Respuesta determinista (sin IA)»). Presentarlo como fortaleza. |
| **El servidor local no arranca** | Activar el venv, correr `pip install -r backend/requirements.txt` y mostrar mientras tanto las capturas de `docs/screenshots/`. |
| **El puerto 8000 está ocupado** | `--port 8010` y abrir ese puerto. |
| **Aparece «DATOS SINTÉTICOS»** | Reiniciar sin `INTIMAP_DATASET`, o explicar que es el modo de respaldo. |
| **El proyector tiene poca resolución** | Zoom al 80–90%. En pantallas angostas la leyenda pasa debajo del mapa y los paneles se apilan. |

## Preguntas probables del jurado
- **«¿Qué tan precisos son los datos?»** Son climatología de 25 años de NASA POWER con resolución de 0,5° a 1°: celdas vecinas pueden compartir valores. Sirven para comparar zonas, no para diseñar una planta.
- **«¿Qué significan los colores?»** Cada capa tiene su propio tono; más oscuro indica mayor puntuación relativa dentro de Jujuy. La leyenda da los cortes numéricos.
- **«¿Por qué no calculan energía eólica?»** Haría falta un modelo de turbina y la distribución de vientos. Mostramos un índice comparativo y lo decimos explícitamente.
- **«¿Usan IA para los cálculos?»** No. Todos los cálculos son deterministas en Python. La IA, si se activa, solo redacta y se descarta si cambia un número.
- **«¿Pueden usarlo comercialmente?»** Habría que reemplazar la fuente de altitud (Open-Meteo es no comercial) y confirmar la licencia del IGN.
