# Guía de marca — IntiMap Jujuy

> Estado: **propuesta de la Fase 6A, aún no implementada.** Los valores de color fueron verificados con cálculo de contraste WCAG y con el validador de paletas (ver §4.4).

## 1. Posicionamiento

**Para** municipios, comunidades rurales, cooperativas, instaladores y desarrolladores que necesitan decidir **dónde vale la pena estudiar** un proyecto solar o eólico en Jujuy,
**IntiMap Jujuy es** un mapa de evaluación preliminar
**que** compara las 104 zonas de la provincia con datos climatológicos públicos de 25 años, prioridades ajustables y una simulación solar transparente,
**a diferencia de** los atlas globales y las planillas sueltas,
**porque** habla del territorio jujeño, muestra de dónde sale cada número, dice «No calculable» cuando falta información y funciona sin internet.

**Frase de marca:** *El primer filtro para la energía renovable en Jujuy.*

**Categoría:** herramienta de **prefactibilidad** (comparar y priorizar zonas). **No** es un estudio de factibilidad, de ingeniería ni de recurso.

## 2. Problema, propuesta y diferenciales

| | Contenido |
|---|---|
| **Problema principal** | Decidir dónde estudiar un proyecto renovable exige cruzar datos dispersos y técnicos (irradiación, viento, altitud, temperatura) en una provincia muy diversa. Hoy ese primer filtro depende de consultores o de herramientas globales poco localizadas. |
| **Propuesta de valor** | En minutos, comparar zonas de Jujuy por potencial solar y eólico según las prioridades propias, y llevarse una estimación transparente que orienta qué estudiar después. |
| **Diferenciales (reales, implementados)** | 1) Toda la provincia en 104 zonas de unos 28 km con contorno oficial del IGN. 2) Procedencia visible en cada dato: descargado, calculado o sintético. 3) Corrección por altitud: la densidad del aire en la Puna reduce el rendimiento eólico. 4) Prioridades que recalculan el ranking al instante. 5) Simulador que no inventa: muestra «No calculable» cuando falta un dato. 6) Asistente que responde con los números del mapa y funciona sin IA. 7) Funciona sin conexión. |

### Usuarios objetivo y beneficio principal
| Usuario | Necesidad | Beneficio que comunicamos |
|---|---|---|
| Municipios y comisiones municipales | Priorizar zonas para electrificación o autoconsumo público | «Sepan qué zonas conviene estudiar primero, con datos públicos y trazables.» |
| Comunidades y cooperativas rurales | Entender opciones antes de pedir asesoramiento | «Una primera mirada en lenguaje simple, sin tecnicismos.» |
| Instaladores y desarrolladores | Filtrar zonas antes de visitar un sitio | «Ahorren visitas a zonas que no prometen.» Se dice como orientación, no como certeza. |
| Productores e inversores | Comparar zonas de forma preliminar | «Comparen escenarios con supuestos editables y visibles.» |

### Objeciones previsibles y respuesta honesta
| Objeción | Respuesta |
|---|---|
| «¿Qué tan precisos son los datos?» | Son climatología de 25 años de NASA POWER con resolución de 0,5° a 1°: sirven para comparar zonas, no para diseñar en una parcela. Lo decimos en la herramienta. |
| «¿Me garantiza el ahorro?» | No. La simulación es un escenario hipotético editable con recuperación simple. Para invertir hace falta un estudio de sitio. |
| «¿Por qué no calculan energía eólica?» | Sin modelo de turbina ni distribución de vientos, un número en kWh sería engañoso. Mostramos un índice comparativo. |
| «Ya existen atlas solares y eólicos.» | IntiMap no compite en resolución: aporta foco provincial, prioridades propias, economía transparente y explicación en español. |
| «¿Usan IA para calcular?» | No. Todos los cálculos son deterministas. La IA, si se activa, solo redacta y se descarta si cambia un número. |
| «¿Se puede usar comercialmente?» | Hoy el proyecto es una demo de hackatón. El uso comercial requiere reemplazar la fuente de altitud (Open-Meteo es no comercial) y confirmar la licencia del IGN. |

## 3. Voz y tono
- **Claro, cercano y responsable.** Hablamos de vos, en español rioplatense, sin jerga innecesaria.
- **Honesto sobre el alcance.** Cada número va acompañado de «estimado», «preliminar» o «escenario».
- **Orgullo territorial sin folclore impostado:** Puna, quebradas y Yungas como paisaje y datos, no como decoración.

| ✅ Decir | ❌ No decir |
|---|---|
| «Evaluación preliminar para comparar zonas» | «Estudio de factibilidad», «certificado», «garantizado» |
| «Estimación con datos climatológicos públicos» | «Datos medidos en tu terreno», «precisión de parcela» |
| «Orienta qué zonas estudiar primero» | «Te dice dónde invertir» |
| «Escenario hipotético editable» | «Cotización», «tarifa oficial», «ahorro asegurado» |
| «Impacto potencial» o «puede ayudar a…» | Cifras de impacto social o ambiental no medidas |
| «104 zonas · climatología 2001–2025 · 3 fuentes públicas» (cifras reales) | Usuarios, clientes, ahorros o porcentajes que no existen |

## 4. Identidad visual

### 4.1 Concepto
**«Altura, sol y datos.»** La luz intensa y los colores de tierra de la Puna y las quebradas, ordenados por la **cuadrícula** del mapa. La grilla de celdas de 0,25° es el motivo gráfico propio: es literal al producto, no un préstamo cultural.

### 4.2 Logo (propuesta)
- **Isotipo:** un cuadrado redondeado (una celda de la grilla) con un **sol geométrico de semicírculo** que asoma sobre una **línea de serranía** simple. Se construye con 3 formas en SVG y se lee bien a 16 px.
- **Logotipo:** «Inti**Map**» con «Map» en verde energía, más «JUJUY» en versalitas con espaciado amplio debajo o al lado.
- **Usos:** fondo arena o blanco (versión color) y fondo verde profundo (versión invertida). Área de respeto igual a la altura de la «I».
- **Sensibilidad:** «Inti» significa «sol» en quechua y también nombra a una deidad andina. Por eso el sol del logo es **abstracto y geométrico**, **sin rostro**, y no imita el Sol de Mayo ni representaciones ceremoniales.

### 4.3 Recursos culturales — qué evitamos
No usamos símbolos comunitarios o sagrados sin fundamento ni consulta:
- Wiphala, chakana o cruz andina, rostros del sol.
- Apachetas, imaginería de Pachamama.
- Motivos de tejidos o aguayos de comunidades específicas.
- Diablos de carnaval.

**Sí usamos:** perfiles genéricos de montaña, el sol geométrico, la grilla y la paleta de tierra y vegetación como referencia al paisaje.

### 4.4 Paleta

#### Colores de marca (verificados)
| Token | Hex | Uso | Contraste verificado (WCAG 2) |
|---|---|---|---|
| `--im-green-900` (verde profundo) | `#112B29` | Fondos oscuros (hero, header de la herramienta, footer) y texto de títulos | 13,29:1 sobre arena (AAA) |
| `--im-green-700` (verde acción) | `#1F6553` | **Botones primarios**, enlaces y foco | Blanco encima 6,90:1 (AA) · sobre arena 6,12:1 |
| `--im-green-500` (verde energía) | `#277B68` | Acentos, íconos, «Map» del logotipo. Texto solo si es grande o en negrita | 4,52:1 sobre arena (AA justo) · blanco encima 5,10:1 |
| `--im-sun-400` (solar dorado) | `#D9A441` | **Solo rellenos**: CTA secundario, destacados, sol del logo | ❌ 2,00:1 como texto sobre arena. ✅ Texto verde profundo encima: 6,66:1 |
| `--im-sun-700` (dorado texto) | `#8A6212` | Texto dorado sobre claro, si hace falta | 4,86:1 sobre arena (AA) |
| `--im-clay-500` (terracota) | `#C56F4F` | Ilustración, bordes y decoración | ❌ 3,23:1 como texto normal (solo texto grande o UI) |
| `--im-clay-700` (terracota texto) | `#A4553A` | Avisos y texto terracota sobre claro | 4,73:1 sobre arena (AA) |
| `--im-sand-50` (arena) | `#F5F1E8` | Fondo general | — |
| `--im-ink` (tinta) | `#1B2422` | Texto de cuerpo | 14,09:1 sobre arena (AAA) |
| `--im-ink-muted` | `#5A625F` | Texto secundario | 5,57:1 sobre arena · 6,27:1 sobre blanco (AA) |
| `--im-line` | `#DDD6C8` | Bordes y divisores | Decorativo |

**Ajustes respecto de la paleta conceptual:**
- Se agregan variantes «700» de verde, dorado y terracota para texto y botones, porque los tonos conceptuales no alcanzan AA como texto normal.
- El dorado queda reservado a rellenos y nunca se usa como color de texto sobre claro.

#### Colores de estado
Llevan siempre ícono y texto, nunca solo color.

| Estado | Fondo | Texto |
|---|---|---|
| Información y estimación preliminar | `#E6EEF0` | `#1E4A5A` |
| Advertencia (supuesto o dato faltante) | `#FBF0D9` | `#7A5200` |
| Error y datos sintéticos | `#F8E1DA` | `#8C2F1C` |
| Éxito y dato descargado | `#E3F0E8` | `#1D5E3A` |

Contrastes verificados: información 8,18:1 · advertencia 6,12:1 · error 6,61:1 · éxito 6,59:1 (todos AA).

#### Escalas del mapa (datos)
El índice de 0 a 100 es una **magnitud**, así que requiere una **escala secuencial de un solo tono, de claro a oscuro**. La escala rojo-amarillo-verde actual es divergente y **falla** el validador de paletas en tres puntos:
- No es monótona en luminosidad: L = 0,58 → 0,91 → 0,60.
- Su extremo claro tiene 1,10:1 de contraste contra el fondo.
- Abarca 123° de tono.

Propuesta, con 5 clases (0–20, 20–40, 40–60, 60–80 y 80–100), **validada**: luminosidad monótona, saltos visibles, extremo claro ≥ 2:1 sobre arena y un solo tono.

| Capa | Rampa (claro → oscuro) | Validación |
|---|---|---|
| Potencial solar | `#C9A04F` `#B0842F` `#8E671C` `#6B4C11` `#46310A` | PASS (4/4) |
| Recurso eólico | `#86A9BE` `#6189A2` `#436C86` `#2D5068` `#1A3346` | PASS (4/4) |
| Puntaje combinado | `#7AB09A` `#579A82` `#3A7F6A` `#235F51` `#123A33` | PASS (4/4) |
| Sin dato o sin pesos | `#B9B3A6` con trama diagonal | Neutro, fuera de las rampas |

> Las rampas eólica y combinada son cercanas entre sí (ΔE 8,5). Es aceptable porque **nunca se muestran juntas** y la leyenda siempre nombra la capa. Ese nombre es la codificación secundaria y es **obligatorio**.
>
> Con esto el mapa también deja de depender del contraste rojo-verde, que confunde a personas daltónicas (un riesgo registrado desde la Fase 2).

### 4.5 Tipografía
| Rol | Fuente | Licencia y entrega |
|---|---|---|
| Títulos y logotipo | **Outfit** (geométrica, cálida y legible), pesos 500, 600 y 700 | SIL Open Font License 1.1. **Autoalojada** en `frontend/assets/fonts/` con su `OFL.txt`, sin Google Fonts en ejecución, para preservar el modo offline. |
| Cuerpo e interfaz | Pila del sistema: `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` | Sin descarga y con rendimiento máximo |
| Cifras | Misma pila, con `font-variant-numeric: tabular-nums` | — |

Escala tipográfica (rem, base 16 px):

| Nivel | Tamaño |
|---|---|
| Display | 3,0 (2,25 en móvil) |
| H1 | 2,25 |
| H2 | 1,75 |
| H3 | 1,25 |
| Cuerpo | 1,0 |
| Pequeño | 0,875 |
| Micro | 0,75 |

Altura de línea: 1,5 en el cuerpo y 1,15 en los títulos.

### 4.6 Espaciado, radios y sombras
- **Espaciado (base 4 px):** `--im-space-1..8` = 4, 8, 12, 16, 24, 32, 48 y 64 px. Secciones de la landing: 64 px en escritorio y 40 px en móvil.
- **Radios:** 6 px en controles, 12 px en cards y 999 px en píldoras y etiquetas.
- **Sombras:** dos niveles suaves (`0 1px 2px rgb(17 43 41 / .08)` y `0 8px 24px rgb(17 43 41 / .10)`). Sin sombras duras.
- **Ancho máximo del contenido en la landing:** 1.120 px. La herramienta mantiene su layout de 3 columnas a pantalla completa.

### 4.7 Componentes
| Componente | Especificación |
|---|---|
| **Botón primario** | Fondo `--im-green-700`, texto blanco y peso 600; padding 12 × 20 px; radio 6 px. Hover `#185344` (blanco encima: 8,90:1). Foco con anillo de 3 px `--im-sun-400` y separación de 2 px. |
| **Botón secundario (CTA dorado)** | Fondo `--im-sun-400` y texto `--im-green-900` (6,66:1). Hover `#C99234` (texto: 5,45:1). |
| **Botón fantasma** | Borde de 1,5 px `--im-green-700`, texto `--im-green-700` y fondo transparente. Sobre fondos oscuros: borde y texto arena. |
| **Card** | Fondo blanco, borde de 1 px `--im-line`, radio 12 px, padding de 24 px y sombra de nivel 1. Ícono en un círculo de 40 px con fondo arena y trazo `--im-green-500`. |
| **Etiqueta de calidad** | Píldora con texto de 0,7 rem: descargado (éxito), calculado (información), sintético o faltante (error) e hipotético (advertencia). Siempre con texto. |
| **Aviso** | Barra con ícono, texto y fondo de estado. El aviso de «estimación preliminar» es permanente en la herramienta. |
| **Navegación** | Barra de 64 px. En la landing es transparente sobre el hero y pasa a sólida al hacer scroll. En la herramienta es `--im-green-900` con el logo invertido. Enlaces: Inicio · Mapa · Metodología · GitHub. En móvil, menú de hamburguesa accesible (`<button aria-expanded>`). |
| **Foco y accesibilidad** | Todos los interactivos con `:focus-visible` y anillo dorado; objetivos táctiles de al menos 44 px; respetar `prefers-reduced-motion`. |

### 4.8 Iconografía
- Íconos de trazo de 1,75 px en caja de 24 px, del set **Lucide** (licencia ISC), copiados **en línea como SVG**. Se incluye su licencia en `frontend/assets/icons/LICENSE-lucide.txt`.
- **Set mínimo:** sun, wind, map, sliders-horizontal, calculator, message-circle, database, triangle-alert, info, wifi-off, arrow-right, github.
- Sin dependencias ni CDN.

### 4.9 Imágenes
- **Sin fotografías** en esta fase, para no asumir riesgos de licencia. Las imágenes son **capturas reales de la herramienta**, que son material propio, e **ilustraciones SVG propias**: perfiles de serranía, sol geométrico y grilla.
- Si más adelante se suman fotos, deben ser propias o tener licencia verificada (por ejemplo CC BY con atribución) y quedar registradas en un `CREDITS.md`.

## 5. Aplicación a la landing y a la herramienta
| Elemento | Landing (`/`) | Herramienta (`/mapa/`) |
|---|---|---|
| Fondo | Arena; hero en verde profundo con ilustración | Arena en los paneles; mapa sobre arena (`#EFE9DC`) |
| Navegación | Transparente a sólida, con CTA «Abrir el mapa» | Verde profundo, con logo invertido, «← Inicio» y «Metodología» |
| Tipografía | Outfit en títulos y sistema en el cuerpo | Ídem, con títulos de panel en Outfit 600 |
| Botones | Primario verde y CTA dorado | Primario verde («Preguntar»); los sliders usan el acento verde |
| Mapa | Captura real en un marco tipo «ventana» | Rampas secuenciales por capa (§4.4) y contorno `--im-green-900` |
| Avisos | Bloque «Qué es y qué no es IntiMap» | Cartel permanente de estimación preliminar, etiquetas de calidad y cartel rojo en modo sintético, **sin cambios de contenido** |

Todos los tokens viven en un único archivo, `frontend/assets/brand.css`, como variables CSS (`--im-*`) que comparten las dos páginas.
