# Ficha del laboratorio

Completar antes del ensayo o recibir del instructor. Los marcadores `<...>` no son valores ejecutables.
No guardar contraseñas, tokens ni cadenas de conexión con secretos.

## Modalidad y responsables

| Campo | Valor |
|---|---|
| Modalidad | `guiada` / `laboratorio individual aislado` |
| Participante o equipo | <alias> |
| Instructor responsable | <responsable> |
| Fecha del ensayo | <fecha> |
| Revisión del framework | `f0f2551` / <revision_ensayada> |
| Biblioteca | `0.2.0` |
| Runtime Fabric ensayado | <runtime> |
| Proyecto generado | <nombre_proyecto> |
| Carpeta local nueva | <ruta_proyecto> |
| Entorno | `dev` |
| Workspace de datos | <proyecto>-datos-dev |
| Workspace de ingeniería | <proyecto>-ing-dev |
| Workspace de analítica | <proyecto>-ana-dev |
| Environment | `env_fwk` |
| SQL servidor FQDN | <servidor>.database.windows.net |
| SQL base dedicada | <base_laboratorio> |
| Esquemas de lakehouse | `dbo` / sin esquemas |
| Prefijo de lotes Run | <R> |
| Cliente seleccionado | <cliente_demo> |
| Ciudad original | <ciudad_original> |
| Línea con importe negativo | <linea_negativa> |
| Línea con importe NULL | <linea_importe_nulo> |
| Línea con motivo NULL 1 | <linea_motivo_nulo_1> |
| Línea con motivo NULL 2 | <linea_motivo_nulo_2> |
| N / R1 / R2 medidos en SQL | <conteos> |

Los IDs de workspace/Environment se entregan al responsable de publicación y se introducen en variables de entorno.
La identidad de SQL de lectura puede ser distinta de la que publica o modifica las filas de la demo.
Registrar cuál ejecuta los notebooks y cuál ejecuta los pipelines.

## Registro de ejecución

| Fase | Batch ID | Contrato | Resultado / evidencia |
|---|---|---|---|
| CRM completa | <R>-crm-01 | 1 | |
| Devoluciones Q1 | <R>-dev-q1 | 1 | |
| Revalidación Q2 | <R>-dev-q2 | 2 | |
| Q3 fallido y recuperación Q4 | <R>-dev-q3 | 3 → 4 | |
| Primer incremental | <R>-crm-02 | 1 | |
| Ventana con posible solape | <R>-crm-03 | 1 | |
| Ventana vacía posterior | <R>-crm-04 | 1 | |
| Activación SCD2 | <R>-crm-scd0 | gold 2 | |
| Barcelona → Valencia | <R>-crm-scd1 | gold 2 | |
| Valencia → Barcelona | <R>-crm-scd2 | gold 2 | |

Un reintento mantiene el identificador original. Un lote nuevo lleva otro ID. Un nuevo prefijo no borra el estado anterior.
Compartir un workspace de datos exige un único escritor; cambiar solo `Run` no aísla a los participantes.
