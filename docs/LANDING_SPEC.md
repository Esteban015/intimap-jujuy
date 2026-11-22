# Especificación de la landing y de la unificación visual — IntiMap Jujuy

> Estado: **propuesta de la Fase 6B, aún no implementada.** La identidad visual está en [`BRAND_GUIDELINES.md`](BRAND_GUIDELINES.md). Todas las cifras de los textos son **reales y verificables** (ver §4); no se usan métricas ficticias.

## 1. Arquitectura de páginas

| Ruta | Contenido | Archivo |
|---|---|---|
| `/` | **Landing** comercial | `frontend/index.html` (nuevo contenido) |
| `/mapa/` | **Herramienta** actual (mapa, sliders, ficha, simulador y asistente) | `frontend/mapa/index.html` (el `index.html` actual, movido) |
| `/mapa` | Redirección 307 automática a `/mapa/` | Comportamiento nativo de Starlette `StaticFiles(html=True)`, verificado |
| `/api/*`, `/docs` | **Sin cambios** | `backend/app/main.py` no se modifica |

Decisión: se usa una **subcarpeta estática** en lugar de una ruta nueva en FastAPI, así el backend queda intacto. Todos los enlaces internos apuntan a **`/mapa/` con la barra final**, para evitar la redirección. Detrás del proxy de Render, esa redirección podría construirse con `http://` y sumar un salto.

## 2. Landing — estructura y textos

### 2.0 Navegación (fija)
Logo IntiMap · **Cómo funciona** · **Para quién** · **Metodología** · **GitHub**. A la derecha, el botón primario «Abrir el mapa →» que lleva a `/mapa/`.

### 2.1 Hero (fondo verde profundo con ilustración SVG de serranías, sol geométrico y grilla)
- **Antetítulo:** EVALUACIÓN PRELIMINAR DE ENERGÍAS RENOVABLES · JUJUY
- **Título:** **El primer filtro para la energía renovable en Jujuy.**
- **Bajada:** Compará el potencial solar y eólico de toda la provincia, ajustá tus prioridades y descubrí qué zonas conviene estudiar primero. Con datos públicos, transparentes y sin vueltas.
- **CTA primario (dorado):** «Explorar mapa energético» → `/mapa/` (texto aprobado en la Fase 6C) · **CTA secundario (fantasma):** «Cómo funciona» → `#como-funciona`
- **Fila de datos reales:** `104 zonas` · `25 años de climatología` · `3 fuentes públicas` · `Funciona sin internet`
- **Visual:** captura real de la herramienta (`mapa-combinado.png`) en un marco de «ventana», con un sombreado suave.

### 2.2 El problema
- **Título:** Decidir dónde estudiar un proyecto renovable no debería empezar a ciegas.
- **Texto:** La radiación, el viento, la altura y la temperatura cambian mucho entre la Puna, las quebradas y las Yungas. Cruzar esos datos lleva tiempo, conocimientos técnicos y, muchas veces, consultorías costosas solo para saber por dónde empezar.
- Tres bloques breves:
  - **Datos dispersos:** las fuentes existen, pero están en distintos formatos y escalas.
  - **Territorio diverso:** a más de 3.500 m el aire es menos denso y el mismo viento rinde menos.
  - **Decisiones tempranas:** antes de un estudio de sitio, hace falta un primer filtro confiable.

### 2.3 La solución
- **Título:** Un mapa que compara, explica y no exagera.
- **Texto:** IntiMap divide Jujuy en 104 zonas de unos 28 km y calcula para cada una indicadores solares y eólicos preliminares. Vos elegís qué priorizar; el mapa se reordena al instante.
- **Visual:** captura de la ficha y el simulador (`ficha-simulador.png`).

### 2.4 Funcionalidades (cards con ícono, todas implementadas)
| Ícono | Título | Texto |
|---|---|---|
| map | Mapa de toda la provincia | 104 zonas recortadas al contorno oficial del IGN, con capas de potencial solar, recurso eólico y puntaje combinado. |
| sliders-horizontal | Tus prioridades, al instante | Ajustá el peso de lo solar y lo eólico; el ranking y los colores se recalculan en tu navegador. |
| sun | Ficha de cada zona | Irradiación, temperatura, viento a 50 m, altitud y densidad del aire, con la indicación de qué fue descargado y qué fue calculado. |
| calculator | Simulador solar transparente | Potencia, costo, valor de la energía y autoconsumo editables. Si falta un dato, dice «No calculable». |
| message-circle | Asistente que explica | Respuestas con los números del mapa, en lenguaje simple y siempre con advertencias. Funciona sin IA. |
| wifi-off | Funciona sin conexión | Los datos ya están preparados: la herramienta no depende de servicios externos para funcionar. |

### 2.5 Cómo funciona (`#como-funciona`, 3 pasos)
1. **Elegí qué priorizar.** Mové los controles solar y eólico; el mapa muestra qué zonas se destacan.
2. **Explorá una zona.** Tocá una celda para ver sus datos, su recomendación preliminar y una estimación de generación solar.
3. **Simulá y preguntá.** Probá un escenario económico editable y consultá al asistente por qué esa zona se destaca.

### 2.6 Para quién (`#para-quien`)
- **Municipios e instituciones:** para priorizar zonas antes de encargar estudios.
- **Comunidades y cooperativas:** para tener una primera mirada clara antes de pedir asesoramiento.
- **Instaladores y desarrolladores:** para filtrar zonas antes de visitar un sitio.
- **Productores e inversores:** para comparar zonas con supuestos visibles.

### 2.7 Impacto potencial
- **Título:** Información pública al servicio de decisiones locales.
- **Texto:** IntiMap **puede ayudar** a que municipios y comunidades lleguen mejor preparados a la conversación con especialistas: con preguntas más precisas, zonas candidatas y supuestos explícitos. **Es una herramienta de orientación; su impacto todavía no fue medido.**
- No se publican cifras de impacto, usuarios ni ahorros.

### 2.8 Qué es y qué no es (bloque destacado, obligatorio)
| ✅ IntiMap es | ❌ IntiMap no es |
|---|---|
| Una evaluación preliminar para comparar zonas | Un estudio de factibilidad o de ingeniería |
| Indicadores relativos dentro de Jujuy (de 0 a 100) | Una certificación de viabilidad o de aptitud del terreno |
| Estimaciones con datos climatológicos de unos 28 km | Una medición de tu parcela |
| Un escenario económico editable con recuperación simple | Una cotización, una tarifa oficial ni una rentabilidad garantizada |
| Un índice comparativo de recurso eólico | Un cálculo de la energía que produciría un aerogenerador |

### 2.9 Metodología y fuentes (`#metodologia`)
- **NASA POWER:** irradiación, temperatura y viento a 50 m; climatología de enero de 2001 a diciembre de 2025.
- **Open-Meteo / Copernicus DEM:** altitud (uso no comercial, CC BY 4.0).
- **IGN Argentina:** contorno provincial oficial.
- Enlaces a `docs/DATA_METHODOLOGY.md` y al repositorio en GitHub. Son enlaces externos opcionales: la página no depende de ellos para cargar.

### 2.10 CTA final
- **Título:** Empezá por el mapa.
- **Texto:** Explorá las 104 zonas de Jujuy y descubrí cuáles conviene estudiar primero.
- **Botón dorado:** «Explorar mapa energético» → `/mapa/`

### 2.11 Footer
- Logo, frase de marca y «Proyecto del hackatón Tren Solar · Jujuy 2026».
- **Atribuciones:** NASA POWER · Open-Meteo (CC BY 4.0) · Copernicus DEM · IGN Argentina · Leaflet (BSD-2) · Lucide (ISC) · Outfit (OFL).
- **Aviso legal breve:** «Estimaciones preliminares con fines orientativos. No reemplazan estudios de sitio, mediciones ni asesoramiento profesional.»
- Enlaces: Mapa · Metodología · GitHub.

## 3. Herramienta (`/mapa/`) — unificación visual sin cambios funcionales

| Cambio | Detalle | Qué **no** cambia |
|---|---|---|
| Header | Barra verde profundo con el logo invertido, «← Inicio» (`/`), «Metodología» y el cartel de estimación preliminar, que se conserva | El texto y la lógica del cartel; el cartel rojo del modo sintético |
| Tokens | `styles.css` pasa a usar las variables `--im-*` de `assets/brand.css` | Layout de 3 columnas y comportamiento responsive |
| Escalas del mapa | Rampas secuenciales por capa (BRAND_GUIDELINES §4.4) en lugar de rojo-amarillo-verde; leyenda con el nombre de la capa, cortes 0/20/40/60/80/100 y «bajo/alto» | Los cortes de clase, los valores, la normalización y `scoring.js` |
| Componentes | Botones, etiquetas de calidad, avisos y cards con los estilos de la marca | Los textos de advertencia, las etiquetas «descargado» y «calculado», y «No calculable» |
| Tipografía | Outfit autoalojada en los títulos de panel | — |

**Archivos de la herramienta que se tocan:**
- `frontend/mapa/index.html` (movido).
- `frontend/styles.css`, solo estilos.
- `frontend/app.js`, **únicamente** en la constante de colores `BINS`/`NO_DATA` (que pasa a ser una rampa por capa) y el HTML de la leyenda.

**No se tocan:** `scoring.js`, las llamadas a la API, el simulador, el asistente ni el backend.

## 4. Fuente de cada cifra pública
| Cifra | Fuente verificable |
|---|---|
| 104 zonas | `data/processed/cells.geojson` (`metadata.counts.cells`) |
| ~28 km | Celdas de 0,25° (`grid_resolution_deg`) |
| 25 años (2001–2025) | `metadata.climate_period` (respuesta de NASA POWER) |
| 3 fuentes públicas | NASA POWER, Open-Meteo y el IGN (`data/SOURCES.md`) |
| Funciona sin internet | Verificado en las Fases 2 a 5: 0 requests externos |
| 3.500 m (Puna) | Rango de altitud del dataset: 334 a 5.258 m |

## 5. Plan técnico

### 5.1 Estructura de archivos (propuesta)
```
frontend/
  index.html                 ← landing (nuevo contenido)
  landing.css                ← estilos propios de la landing
  mapa/index.html            ← herramienta (movida; rutas absolutas /app.js, /styles.css, /vendor/...)
  app.js, scoring.js         ← sin mover (scoring.js sin cambios)
  styles.css                 ← herramienta, reescrita sobre los tokens
  vendor/leaflet/            ← sin cambios
  assets/
    brand.css                ← tokens --im-* + base + componentes compartidos
    logo.svg, logo-inverse.svg, favicon.svg
    fonts/Outfit-*.woff2 + OFL.txt     ← autoalojada (solo subconjunto latino, 3 pesos)
    icons/LICENSE-lucide.txt           ← íconos en línea como SVG en el HTML
    img/mapa-combinado.png, ficha-simulador.png   ← copias de docs/screenshots (material propio)
```

### 5.2 Reglas
- **Sin frameworks ni dependencias nuevas** de Python o JS. La única descarga es la fuente Outfit (OFL), una sola vez, para autoalojarla.
- **Sin requests externos en ejecución:** fuentes, íconos e imágenes son locales; los enlaces a GitHub son navegación, no recursos.
- **La landing no carga Leaflet ni datos**: es HTML y CSS con un JS mínimo para el menú móvil y el estado de la navegación al hacer scroll.
- **Accesibilidad:** contraste AA (ya verificado en la paleta), `:focus-visible`, objetivos de al menos 44 px, `prefers-reduced-motion`, `alt` en las capturas y jerarquía de títulos correcta.
- **SEO y compartir:** `<title>`, `meta description` y Open Graph con la captura local (`og:image` relativa a la URL de producción).

### 5.3 Validación prevista (smoke, no una suite)
1. `/` devuelve 200 y renderiza la landing, sin requests externos ni errores de consola, en escritorio (1440) y móvil (390).
2. `/mapa` → 307 → `/mapa/` 200. Los CTA apuntan a `/mapa/`.
3. Regresión completa de la herramienta en `/mapa/`, con los scripts de smoke de las Fases 2 y 3 (con la URL cambiada): 104 celdas, capas, sliders sin requests, ficha, simulador (5,2 años), asistente determinista y modo sample.
4. Las rampas del mapa coinciden con las validadas y la leyenda nombra la capa.
5. `/api/*` y `/docs` siguen iguales (health, cells, simulate y assistant).
6. Contraste de los pares usados realmente y revisión visual de capturas.
7. Producción: smoke posterior al deploy (`docs/DEPLOY_RENDER.md`) más `/` y `/mapa/`.

## 6. Riesgos
| Riesgo | Mitigación |
|---|---|
| Romper la herramienta al moverla a `/mapa/`, por rutas relativas | Rutas absolutas y regresión completa con los scripts existentes |
| Los enlaces o marcadores viejos a `/` esperan la herramienta | La landing tiene el CTA «Abrir el mapa» en el hero y en la navegación |
| Redirección `http` detrás del proxy en `/mapa` | Enlaces internos siempre a `/mapa/` |
| Cambiar la escala de colores altera la lectura del mapa | Mismos cortes de clase y leyenda explícita. Las capturas y el guion de demo (`DEMO_SCRIPT.md`) deben actualizarse |
| Promesas de marketing excesivas | Bloque «Qué es y qué no es», cifras con fuente (§4) y lista de frases prohibidas (BRAND_GUIDELINES §3) |
| Peso de la fuente | Solo el subconjunto latino y 3 pesos (unos 60–90 KB en total); `font-display: swap` |
| Uso del nombre «Inti» | Sol geométrico sin rostro; se sugiere validar la marca con referentes locales |
| Licencias | OFL (Outfit), ISC (Lucide) y BSD-2 (Leaflet), con licencias incluidas; sin fotos de terceros |
