# Fuentes de datos — IntiMap Jujuy

Todas las descargas se hacen con los scripts de preparación. **La app no llama a ninguna API en ejecución.**
Las respuestas originales quedan en `data/raw/` (sin secretos: ninguna de estas fuentes usa clave).

| Dato | Fuente | URL | Período / resolución | Unidades | Condiciones de uso |
|---|---|---|---|---|---|
| Contorno de Jujuy | IGN Argentina, WFS `ign:provincia` (oficial) | https://wms.ign.gob.ar/geoserver/ign/ows | Versión vigente al descargar (ver `fetched_at`) | EPSG:4326 | Licencia de uso del IGN con atribución obligatoria. Los términos exactos están **A CONFIRMAR** en https://www.ign.gob.ar/NuestrasActividades/InformacionGeoespacial/CapasSIG |
| Contorno (respaldo, no se usó) | geoBoundaries gbOpen ARG ADM1 | https://www.geoboundaries.org | Origen Wikimedia, año 2006, **NO oficial** | — | CC BY 2.5 |
| GHI, temperatura, viento a 50 m | NASA POWER Climatology API, comunidad RE (`ALLSKY_SFC_SW_DWN`, `T2M`, `WS50M`, media anual `ANN`) | https://power.larc.nasa.gov/docs/services/api/temporal/climatology/ | Climatología de 25 años, ene-2001 a dic-2025. Resolución nativa: solar ~1°, meteorología ~0,5°×0,625° | kWh/m²/día, °C, m/s | Datos públicos de NASA; citar según https://power.larc.nasa.gov/docs/referencing/ |
| Altitud | Open-Meteo Elevation API (Copernicus DEM GLO-90) | https://open-meteo.com/en/docs/elevation-api | DEM de 90 m, en un punto por celda | m | Gratuito **solo para uso no comercial**, con atribución CC BY 4.0 (https://open-meteo.com/en/terms). Un uso comercial requiere plan pago o reemplazar la fuente |

## Limitaciones a comunicar
- La grilla es de 0,25° (~28 km), pero los datos de NASA POWER son más gruesos. Varias celdas vecinas comparten el mismo valor de GHI, temperatura o viento.
- La altitud corresponde a un punto. En zonas de quebrada, la altitud real dentro de la celda varía cientos o miles de metros.
- `wind_power_density_w_m2` usa la velocidad media. Es un índice comparativo, no la densidad de potencia real ni la energía de una turbina.
- El área de cada celda es aproximada (grados² × cos(lat)).
