# Contexto para Cursor: Mapa de potencial renovable de Jujuy

> Pegalo como primer prompt o guardalo como AGENTS.md en la raíz del repo. Hackatón de un día, sin hardware.


## 1. Instrucciones para la IA

- Actuá como ingeniero senior que me ayuda a construir un MVP en unas 8 horas. Priorizá que funcione de punta a punta antes de pulir.
- Trabajá por fases (sección 12). Al terminar cada fase, ejecutá la app y verificá que corre antes de seguir.
- Código simple y legible. Sin autenticación, sin microservicios, sin sobreingeniería.
- El demo debe funcionar offline con datos cacheados. Las APIs externas se usan solo en scripts de preparación, nunca en tiempo de ejecución.
- Textos de la interfaz y comentarios en español. Nombres de variables y código en inglés.
- No inventes datos. Si falta uno, usá un valor marcado como "estimado" y dejá un TODO.
- Las claves van en .env y nunca se suben al repo.
- Si algo es ambiguo, elegí la opción más simple y anotala en DECISIONS.md.

## 2. Qué es el producto

Un mapa interactivo de Jujuy que responde: ¿dónde conviene instalar energía renovable y por qué?
Divide la provincia en una grilla, calcula un puntaje de potencial por celda (solar, viento y otros factores), permite ajustar prioridades con deslizadores y tiene un asistente de IA que justifica la recomendación con números.
No es un monitor de paneles. Resuelve la decisión previa a instalar.

## 3. Usuarios y casos de uso

- Instalador o empresa: "¿Dónde conviene instalar solar para una planta que consume X?"
- Comunidad o municipio: "¿Qué zona rural conviene electrificar primero?"
- Inversor o minera: "Comparar dos zonas por generación estimada y retorno."

## 4. Alcance del MVP

Obligatorio
1.  Mapa de Jujuy con celdas coloreadas por puntaje (de rojo a verde).
2.  Capas activables: solar, viento, puntaje total.
3.  Al tocar una celda: ficha con datos, recomendación (solar, eólica o mixta) y estimación de generación anual y retorno.
4.  Deslizadores de prioridades que recalculan el mapa al instante.
5.  Asistente de IA con preguntas libres, que responde con los números de las celdas.
6.  Aviso visible de que son estimaciones preliminares y de dónde salen los datos.
Deseable (solo si sobra tiempo)
- Comparar dos celdas lado a lado.
- Exportar la ficha de una zona a PDF.
- Capa de cercanía a red eléctrica y caminos.
Fuera de alcance Usuarios y login, pagos, datos en tiempo real, hardware, app móvil.

## 5. Stack

- Frontend: Next.js (App Router) + TypeScript + Tailwind + Leaflet (react-leaflet).
- Backend: FastAPI (Python) + pandas + shapely.
- Datos: archivos JSON/GeoJSON en data/. Sin base de datos.
- IA: un cliente de LLM detrás de una interfaz propia. Variables LLM_API_KEY y LLM_MODEL en .env. Si no hay clave, el asistente responde con una plantilla basada en reglas.
- Mapa sin conexión: no depender de tiles online. Dibujar celdas y contorno de Jujuy sobre fondo liso. Si hay internet, se puede mostrar una capa base de OpenStreetMap con degradación elegante.

## 6. Estructura del repo

```text
/
├── AGENTS.md
├── DECISIONS.md
├── .env.example
├── data/
│   ├── jujuy.geojson          # contorno de la provincia
│   ├── cells_raw.json         # datos crudos por celda
│   ├── cells.geojson          # celdas con métricas ya normalizadas
│   └── towns.json             # localidades (nombre, lat, lon, aprox.)
├── scripts/
│   ├── build_grid.py          # genera la grilla y la recorta al contorno
│   ├── fetch_data.py          # baja datos de las APIs y los cachea
│   └── make_synthetic.py      # datos sintéticos de respaldo
├── backend/
│   ├── main.py
│   ├── scoring.py
│   └── assistant.py
└── frontend/
```

    └── (app Next.js)

## 7. Datos

Grilla. Celdas de 0,25° (unos 28 km) sobre la caja aproximada de Jujuy: latitud de -21,8 a -24,4 y longitud de -67,2 a -64,1. Recortar con el contorno de la provincia (shapely). Rinde unas 90 a 120 celdas, suficiente para un demo.
Variables por celda (centroide):
- Irradiación solar global horizontal media anual (kWh/m²/día).
- Velocidad del viento a 50 o 100 m (m/s).
- Temperatura ambiente media (°C).
- Altitud (m).
Fuentes (todo gratuito, descargar antes del evento):
- NASA POWER, endpoint de climatología puntual (power.larc.nasa.gov, comunidad RE), con irradiación, viento y temperatura. Verificar nombres de parámetros en su documentación.
- Open-Meteo, que devuelve altitud y también viento y temperatura.
- Contorno de provincias: Natural Earth o geoBoundaries.
Regla clave: fetch_data.py consulta las APIs una sola vez y guarda todo en data/cells_raw.json. Si falla la red, make_synthetic.py genera datos plausibles (más sol y altura hacia el oeste y la Puna, más viento en zonas altas) y los marca con "synthetic": true. La interfaz muestra un cartel si los datos son sintéticos.
Opcional (si hay tiempo): líneas eléctricas y caminos exportados de OpenStreetMap en preparación, para calcular distancia a infraestructura. Si no están, el peso de ese factor queda en 0.
Localidades: towns.json con San Salvador de Jujuy, Palpalá, Libertador General San Martín, Perico, San Pedro, Tilcara, Purmamarca, Humahuaca, Tumbaya, Abra Pampa, La Quiaca, Susques y Volcán. Usar coordenadas aproximadas y marcarlas como tales.

## 8. Modelo de puntaje

Todo se calcula en scoring.py (y se replica en el frontend para que los deslizadores respondan al instante).
Solar (kWh por kWp por año):
Tcell = Tamb + 20
temp_factor = 1 - 0.004 * (Tcell - 25)
solar_kwh_kwp = GHI_kWh_m2_day * 365 * 0.80 * temp_factor
(0.80 es el performance ratio base. Son aproximaciones y deben figurar como tales.)
Viento (densidad de potencia ajustada por altitud):
rho = 1.225 * (1 - 2.25577e-5 * altitud_m) ** 4.25588
wpd = 0.5 * rho * v ** 3        # W/m²
La menor densidad del aire en la Puna reduce el potencial eólico respecto de lo que sugiere la velocidad sola. Es un detalle que conviene destacar.
Normalización: min-max a 0-100 entre todas las celdas, por variable.
Puntaje total:
score = w_solar*s_solar + w_wind*s_wind + w_grid*s_grid + w_access*s_access
Pesos por defecto: solar 0.6, viento 0.3, red 0.1, acceso 0.0 (se activan solo si existen los datos). Los deslizadores ajustan los pesos y se renormalizan para que sumen 1.
Recomendación por celda:
- Solar si s_solar >= s_wind + 15
- Eólica si s_wind >= s_solar + 15
- Mixta en otro caso
Economía (valores de ejemplo editables en la interfaz):
ahorro_anual = solar_kwh_kwp * tarifa_usd_kwh      # tarifa de ejemplo: 0.10
payback_anios = costo_usd_kwp / ahorro_anual        # costo de ejemplo: 900
Mostrar siempre "valores de ejemplo, ajustables".

## 9. API del backend

- GET /api/cells devuelve un GeoJSON FeatureCollection con las métricas crudas y normalizadas de cada celda, más un indicador synthetic.
- GET /api/towns devuelve la lista de localidades.
- POST /api/assistant recibe {question, selected_cell_id?, weights} y devuelve {answer, cell_ids}.
El recálculo de puntajes con los deslizadores se hace en el cliente, sin llamar al backend.

## 10. Asistente de IA

Cómo se arma el contexto (en assistant.py):
1.  Tomar los pesos actuales y recalcular puntajes.
2.  Incluir la celda seleccionada (si hay) con todas sus métricas.
3.  Incluir las 5 celdas con mejor puntaje y la localidad más cercana a cada una.
4.  Enviar todo al modelo como JSON junto con la pregunta.
Prompt de sistema (usar tal cual):
Sos un asistente de planificación de energías renovables para la provincia de Jujuy, Argentina.
Respondé en español, de forma clara y para personas no técnicas.
Usá SOLO los datos que te paso en el contexto. No inventes cifras ni lugares.
Cada recomendación debe incluir los números que la justifican (irradiación, viento, generación estimada, retorno).
Si falta un dato o la pregunta excede lo que sabés, decilo.
Terminá siempre con una advertencia breve: son estimaciones preliminares que requieren un estudio de sitio.
Formato: 1) Recomendación, 2) Por qué, 3) Advertencia. Máximo 150 palabras.
Sin clave de API: devolver una respuesta armada con una plantilla a partir de la celda y los datos (mismo formato de tres partes), para que el demo nunca falle.

## 11. Interfaz

- Desktop primero, responsive. Mapa a pantalla completa con un panel lateral.
- Panel izquierdo: selector de capas (puntaje total, solar, viento), deslizadores de prioridades y valores económicos de ejemplo.
- Mapa: celdas coloreadas con escala rojo-amarillo-verde y leyenda. Contorno de Jujuy y puntos de localidades. Click en una celda para seleccionarla.
- Panel derecho: ficha de la celda (altitud, irradiación, viento, generación estimada, recomendación, retorno) y el chat del asistente con preguntas sugeridas, por ejemplo "¿Dónde conviene instalar solar para una comunidad de 50 familias?".
- Cartel visible: "Estimaciones preliminares. Fuente: NASA POWER / Open-Meteo" (o "Datos sintéticos de demostración" si corresponde).
- Estado de carga y manejo de errores en todas las llamadas.

## 12. Plan por fases

Fase
Tiempo
Entregable
0. Base
30 min
Repo, Next.js y FastAPI corriendo, .env.example, DECISIONS.md
1. Datos
1 h
Grilla, fetch_data.py, make_synthetic.py, cells.geojson
2. Puntaje y API
1 h
scoring.py, endpoints /api/cells y /api/towns
3. Mapa
1,5 h
Celdas coloreadas, capas, ficha, deslizadores
4. Asistente
1,5 h
Contexto, prompt, chat, modo sin clave
5. Pulido
1 h
Avisos, leyenda, errores, preguntas sugeridas, ensayo del demo
Reserva
1 h
Imprevistos
Para cada fase: pedir el cambio, ejecutarlo, revisar el diff y probar antes de continuar.

## 13. Criterios de aceptación

- La app arranca con un solo comando por servicio y funciona sin internet.
- El mapa muestra celdas de Jujuy con puntajes coherentes (la Puna destaca en solar).
- Mover un deslizador recalcula colores en menos de un segundo.
- Tocar una celda muestra la ficha completa y una recomendación.
- El asistente responde con números tomados de los datos y termina con la advertencia.
- Sin clave de API o sin red, el asistente igual responde.
- Ningún secreto en el repo.

## 14. Guion del demo (2 minutos)

1.  Problema (15 s): decidir dónde instalar renovables en Jujuy hoy exige consultores caros y datos dispersos.
2.  Mapa (30 s): puntaje total de la provincia y la Puna resaltada.
3.  Prioridades (30 s): cambiar un deslizador y ver el mapa recalcularse.
4.  Zona (20 s): tocar una celda y mostrar generación estimada y retorno.
5.  Asistente (20 s): preguntar "¿dónde instalar solar para una comunidad de 50 familias?" y leer la respuesta con números.
6.  Cierre (15 s): cómo se gana dinero (informes para empresas y derivación de clientes a instaladores locales).

## 15. Riesgos y reglas

- Las estimaciones son simplificadas: mostrarlo siempre y no prometer exactitud.
- Los datos crudos tienen resolución gruesa (decenas de km): aclararlo en la interfaz.
- No bloquear el demo por una API: todo cacheado y con plan B sintético.
- Antes de presentar, probar el flujo completo sin conexión.
