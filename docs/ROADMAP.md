# Roadmap — IntiMap Jujuy

Las secciones separan lo **implementado** (rama `feature/intimap-mvp`, PR #1) de lo **propuesto**. Nada de lo propuesto existe todavía.

## 1. MVP implementado ✅
- Contorno oficial del IGN y grilla de 104 celdas de 0,25° recortadas a Jujuy.
- Dataset con NASA POWER (GHI, temperatura y viento a 50 m; climatología 2001–2025) y Open-Meteo (altitud), con procedencia y calidad por campo, y caché offline reproducible.
- Indicadores: kWh/kWp/año, densidad del aire, índice eólico de 0,5·ρ·v³ y normalización de 0 a 100.
- Mapa Leaflet local con capas combinada, solar y eólica, leyenda y vista móvil.
- Sliders de prioridad solar y eólica con recálculo en el navegador, ranking top 5 y manejo de pesos en cero.
- Ficha de la celda con datos descargados y calculados, y recomendación solar, eólica o mixta (heurística de 15 puntos).
- Simulador solar en USD con escenario hipotético editable, «No calculable», advertencias y limitaciones.
- Asistente determinista de 3 partes con un máximo de 150 palabras, LLM opcional validado y respuesta sin red.
- Modo de datos sintéticos claramente señalizado.

## 2. Mejoras posteriores al hackatón (propuestas)
**Calidad de software**
- Incorporar al repositorio tests automatizados: equivalencia entre `scoring.py` y `scoring.js`, casos del simulador (incluido «No calculable»), intenciones del asistente y un smoke del navegador. Durante el hackatón esas pruebas se hicieron como scripts externos.
- CI en GitHub Actions con esos tests.
- Probar el modo LLM contra la API real y medir latencia y tasa de descarte por el validador de números.
- Detección de intención del asistente más robusta que las palabras clave.

**Producto**
- Comparar dos zonas lado a lado (deseable en el spec).
- Exportar la ficha a PDF (deseable en el spec).
- Puntos de localidades en el mapa (`towns.json` y `GET /api/towns` del spec), con coordenadas de fuente citada.
- Paleta de colores apta para daltonismo como opción.
- Despliegue público. Hoy no hay ninguna URL de despliegue.

## 3. Posibles integraciones de datos (propuestas)
| Dato | Uso | Consideraciones |
|---|---|---|
| Líneas eléctricas y subestaciones (OSM u organismos provinciales) | Factor «cercanía a red», hoy deshabilitado | Verificar actualización y licencia. |
| Caminos (OSM) | Factor «acceso» | Licencia ODbL de OSM. |
| Localidades (IGN o INDEC) | Puntos y contexto en la ficha | Fuente oficial con coordenadas. |
| Irradiación de mayor resolución (Global Solar Atlas, NSRDB u otras) | Reducir los bloques de 1° | Revisar licencias y uso comercial. |
| Viento de mayor resolución y distribución (Global Wind Atlas, reanálisis horarios) | Densidad de potencia real y parámetros de Weibull | Necesario antes de cualquier estimación de energía eólica. |
| DEM con licencia comercial (Copernicus GLO-30/90 directo, SRTM) | Reemplazar Open-Meteo | Open-Meteo es solo para uso no comercial. |
| Consumo de comunidades o tarifas de la distribuidora | Dimensionamiento y economía con datos reales | Hoy el escenario es hipotético. |

## 4. Necesidades de validación científica
- **Comparar contra mediciones:** estaciones meteorológicas o solarimétricas en Jujuy, en lugar de satélite y reanálisis.
- **Solar:** pasar de irradiación horizontal a plano inclinado, usar temperatura de celda en horas de sol en lugar de la media de 24 h y revisar el PR de 0,80 para altura y radiación UV de la Puna.
- **Viento:** distribución de velocidades, perfil vertical y rugosidad, curvas de turbina y altura de buje. Recién con eso tiene sentido estimar energía anual.
- **Revisión por especialistas** en energía y en agronomía y territorio (perfil disponible en el equipo) de los textos del asistente y de la heurística de 15 puntos.
- **Sensibilidad:** cómo cambia el ranking con otros pesos, umbrales y resoluciones.

## 5. Posibles modelos comerciales (hipótesis, sin validar)
- Informes preliminares por zona para empresas, municipios o mineras.
- Derivación de interesados a instaladores locales (spec §14).
- Versión institucional para planificación provincial o municipal.

Ninguna de estas hipótesis tiene validación de mercado. Además, un uso comercial requiere resolver primero las licencias de las fuentes (§3).
