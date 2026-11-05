# Plan del instructor · 240 minutos

Modalidad única: cada alumno ejecuta con su propio Fabric. Preparación obligatoria:
[instructores](01_preparacion-instructores.md) y [alumnos](01_antes-de-la-sesion.md).
La guía [Seguir las demos](02_seguir-las-demos.md) contiene los comandos, parámetros de notebook, consultas y resultados
esperados para cada bloque; úsala como guion operativo y documento entregable al alumno.

| Minutos | Duración | Contenido y acción docente | Evidencia al terminar |
|---|---:|---|---|
| 0–15 | 15 | Contratos, capas, workspaces, lógica común; separar extracción, escritura e historia | Alumno localiza fuentes, contratos y modelos |
| 15–50 | 35 | Greenfield real; GUID nuevos, dotenv propio, contratos antes de código, publicación de datos y wheel | Proyecto independiente, recursos y notebooks conectados al Environment |
| 50–75 | 25 | Baseline CRM completa y tipo1; observación, marca e idempotencia | 100 clientes y lote confirmado; repetición sin duplicados |
| 75–115 | 40 | Defectos CSV de origen, Q1, Q2/revalidación, Q3/fallo y Q4/recuperación | 387/10 con Q1; 358/39 con Q2; recuperación del mismo lote Q3 |
| 115–130 | 15 | Descanso | Sesiones y publicación listas para continuar |
| 130–160 | 30 | Completa → incremental, ventana UTC y solape; distinguir filtrado CSV de pushdown SQL | Una modificación, repetición estable y ventana vacía |
| 160–200 | 40 | Ciudad tipo1 → SCD2; contratos de historia/actual, migración explícita y A→B→A | 102 versiones, 100 actuales y tres versiones de C0001 |
| 200–220 | 20 | Consumo de proyección vigente; estructura Cosmos y conservación JSON | Explicar el grano y verificar el volcado Cosmos |
| 220–235 | 15 | Revisión, catálogo, tests, linters, secretos fuera de Git | Diff de contratos y evidencia de checks |
| 235–240 | 5 | Restaurar origen CSV, observar nueva versión y cerrar | Sin perder auditoría ni historia |

La pausa forma parte de las cuatro horas. Descarga de dependencias, alta de capacidad y permisos se resuelven antes.
El final de restauración puede consumir el margen de publicación: inicia la subida al comenzar el último bloque;
si Fabric tarda, registra los lotes pendientes y termina su comprobación antes de cerrar el laboratorio.

Antes de cada demo explica la decisión y muestra el YAML; después ejecuta y contrasta el resultado. En calidad,
avisa del cambio contractual Q1→Q2→Q3→Q4. En SCD2, avisa del cambio de grano y de la nueva proyección vigente.
No atribuyas al framework recuperación de historia previa, detección de borrados ni ahorro físico al leer CSV.

El recorrido SQL conectado de `docs/runbooks/workshop-evolutivo.md` sigue siendo una referencia técnica alternativa
para el instructor; no es la preparación ni el guion entregado a alumnos.

## Tiempos medidos en el ensayo

Ensayo del 4 y 5 de noviembre de 2026 con capacidad Trial FTL4 (West Europe), Runtime 1.3 (Spark 3.5), Environment `env_fwk` con `datafwk` 0.3.0 y una sola sesión de Spark cada vez. «Ejecución» es el tiempo de notebooks y publicación, sin
explicación ni lectura de resultados.

| Bloque | Duración en el plan | Ejecución medida | Margen para explicar |
|---|---:|---|---|
| Demo 1 · greenfield | 35 | ~7 min de publicación (6 del wheel) + vinculación de notebooks | Holgado si la preparación está hecha |
| Demo 2 · completa y tipo1 | 25 | 6 notebooks, ~16 min | Justo |
| Demo 3 · calidad Q1–Q4 | 40 | 6 notebooks, ~11 min | Holgado |
| Demo 4 · incremental | 30 | 9 notebooks, ~22 min | Justo |
| Demo 5 · SCD2 | 40 | 13 notebooks, ~35 min | Insuficiente |
| Demo 6 · consumo y Cosmos | 20 | Consultas, ~5 min | Holgado |
| Demo 7 · revisión | 15 | `pytest` 20 s; `pre-commit` varios minutos la primera vez | Holgado si los hooks ya están instalados |
| Restauración | 5 | No ensayada; ~6 notebooks, 12–15 min | Insuficiente |

Con una capacidad pequeña, las demos 2, 4 y 5 y la restauración no dejan margen. Opciones: publicar el wheel en la
preparación previa, prescindir de las repeticiones de idempotencia (comentarlas sin ejecutarlas), lanzar los notebooks
mientras se explica la teoría o exigir una capacidad mayor que admita sesiones simultáneas.
