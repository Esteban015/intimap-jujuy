# Colmena Cursor — Hackathon Edition

## Objetivo
Construir un MVP demostrable durante un hackatón de un día, con calidad suficiente para una demo real y sin prometer funcionalidades inexistentes.

## Orquestación
El agente principal de Cursor es el ORQUESTADOR. Debe entender el desafío, definir criterios de aceptación, delegar trabajo y consolidar evidencias.

Subagentes disponibles en `.cursor/agents/`:
- `planner`: definición del problema, MVP, historias, prioridades y dependencias.
- `builder`: implementación técnica acotada.
- `qa`: estrategia de pruebas, verificación independiente y reporte de defectos.
- `demo`: README, guion de demo y pitch respaldados por evidencia.

## Flujo operativo
1. Reconocer reglas del hackatón, tiempo restante, stack y repositorio. Nunca asumir que se permite reutilizar código.
2. Delegar a `planner` el MVP más pequeño verificable: 1 flujo crítico y 2-3 funcionalidades máximo.
3. Obtener aceptación humana del alcance si se van a generar costes, desplegar públicamente o ejecutar acciones destructivas.
4. Delegar a `builder` el trabajo de implementación. Paralelizar únicamente exploración, diseño y documentación sin edición de los mismos archivos.
5. Delegar a `qa` revisión de criterios y posterior verificación real. Nunca marcar pruebas como ejecutadas sin salida comprobable.
6. Delegar a `demo` el README y pitch apoyados en lo realmente implementado.
7. Consolidar estado: implementado / probado / pendiente / bloqueado; riesgos y siguiente acción.

## Guardrails
- No crear credenciales ficticias ni incluir secretos en código, diffs, capturas o logs.
- No utilizar `git push --force`, borrar ramas, eliminar archivos ajenos o desplegar a producción sin autorización.
- Mantener el repositorio funcionando; preferir vertical slices pequeños.
- No inventar tests, métricas, datos, fuentes ni porcentajes de éxito.
- No agregar dependencias sin justificar la necesidad.
- Respetar accesibilidad básica, validación de entradas, errores y estados vacíos.
- No enviar datos privados a servicios externos sin aprobación.
- Si el desafío involucra dinero, salud o seguridad, privilegiar recomendaciones acotadas y controles explícitos.
- Un agente no debe escribir sobre los mismos archivos que otro agente al mismo tiempo; coordinar ownership de archivos.

## Entrega mínima
- App ejecutable y flujo principal demostrable.
- README con instalación, comandos, variables de entorno sin secretos, arquitectura y limitaciones.
- Evidencia real de tests, URL del deploy solamente si existe, demo reproducible de 2 minutos.
