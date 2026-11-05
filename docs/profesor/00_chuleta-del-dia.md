# Chuleta del día · viernes 6 de noviembre de 2026

## Comprobación previa

**La víspera**

- [ ] Capacidad del laboratorio de demostración activa y vigente (si es Trial) y asignada a los tres workspaces.
- [ ] Producto y workspaces **nuevos y vacíos** para la demostración en directo; el laboratorio `fsh-alumno99` se
      conserva como referencia y no se reutiliza (no aplicar `checkpoint base` sobre un laboratorio que ya evolucionó).
- [ ] `env_fwk` y workspace de ingeniería en **Runtime 1.3** (Spark 3.5); el valor por defecto 2.0 no está validado.
      `infra/lab/New-LabResources.ps1` lo fija y publica.
- [ ] `az account show`: tenant del laboratorio y **la misma cuenta** que en el portal; nunca una cuenta personal
      (outlook.com, hotmail.com) ni una invitada `#EXT#`.
- [ ] Venv con Python 3.11 o 3.12, `pip` actualizado y `& $Python -m scripts.modificar_csv verificar` correcto.
- [ ] `pre-commit run --all-files` ejecutado una vez, para que los entornos de los hooks ya estén instalados (la
      primera vez tarda varios minutos).
- [ ] Recordatorio al alumnado: preparación completa, SKU de su capacidad y regla de una sesión de Spark cada vez.

**Una hora antes**

- [ ] Iniciar sesión en el portal y en la CLI; abrir los tres workspaces y el SQL analytics endpoint de cada lakehouse.
- [ ] Ninguna sesión de Spark abierta en el laboratorio de demostración.
- [ ] Guía del alumnado proyectable; este manual en segunda pantalla.

## Tiempos por bloque

Ensayo con Trial FTL4 y una sesión de Spark cada vez. «Ejecución» no incluye explicación ni lectura de resultados.

| Minutos | Bloque | Plan | Ejecución medida | Margen |
|---|---|---:|---|---|
| 0–15 | Arquitectura y reglas | 15 | — | — |
| 15–50 | Demo 1 · greenfield | 35 | 33 s local; ~7 min de publicación (6 del wheel) + vinculación | Holgado |
| 50–75 | Demo 2 · completa y tipo1 | 25 | 6 notebooks, ~16 min | Justo |
| 75–115 | Demo 3 · calidad Q1–Q4 | 40 | 6 notebooks, ~11 min | Holgado |
| 115–130 | Descanso | 15 | — | — |
| 130–160 | Demo 4 · incremental | 30 | 9 notebooks, ~22 min | Justo |
| 160–200 | Demo 5 · SCD2 | 40 | 13 notebooks, ~35 min | Insuficiente |
| 200–220 | Demo 6 · consumo y Cosmos | 20 | Consultas, ~5 min | Holgado |
| 220–235 | Demo 7 · revisión | 15 | `pytest` 20 s; `pre-commit` varios minutos la primera vez | Holgado con hooks instalados |
| 235–240 | Restauración y cierre | 5 | No ensayada; ~6 notebooks, 12–15 min estimados | Insuficiente |

Cada notebook tardó entre 90 y 135 s (casi todo arranque de sesión) y unos 60 s más con un error 430.

## Si se va con retraso: opciones (decisión pendiente)

Las cuatro primeras proceden del plan; las demás son propuestas de este manual. Ninguna está decidida.

| Opción | Dónde ahorra | Coste |
|---|---|---|
| A · Publicar el wheel en la preparación previa | ~6 min de la demo 1, que pasan a holgura general | Más preparación para el alumnado |
| B · Comentar sin ejecutar las repeticiones de idempotencia | Demo 2: 3 ejecuciones; demo 3: 1; demo 4: 3; demo 5: 4 | Se pierde la comprobación práctica |
| C · Lanzar los notebooks mientras se explica la teoría | Solapa espera y explicación en todas las demos | Exige explicar sin el resultado delante |
| D · Exigir una capacidad mayor que admita sesiones simultáneas | Elimina los 430 y permite solapar | Coste y requisito previo para el alumnado |
| E · Restauración como demostración del profesorado o tarea posterior | Los 12–15 min que no caben en 5 | El alumnado no la ejecuta en el taller |
| F · Demo 6 con el resultado del laboratorio de referencia si no se llegó a SCD2 | Evita ponerse al día (18 ejecuciones) | Se consulta un laboratorio ajeno |

## Incidencias más probables

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `TooManyRequestsForCapacity` (HTTP 430) | Otra sesión de Spark viva en capacidad pequeña | **Stop session**, esperar un minuto y reintentar con el mismo lote |
| El SQL endpoint no muestra tablas | Metadatos sin sincronizar | Pulsar **Refresh** en el SQL analytics endpoint |
| Workspaces no visibles en el portal o 403 | CLI en otro tenant o con otra cuenta | `az account show`; misma cuenta en portal y CLI |
| La cuenta no entra en Fabric | Cuenta personal de Microsoft | Crear una cuenta de la organización en el tenant |
| Errores raros de tipos en silver | Runtime 2.0 por defecto | Runtime 1.3 en `env_fwk` y en el workspace; publicar de nuevo |
| El notebook usa un `datafwk` antiguo | Environment sin publicar o sesión anterior | Esperar la publicación (~6 min), vincular y reiniciar sesión |
| Cero filas tras cambiar la ciudad | CSV sin publicar, sin esperar o reloj adelantado | `laboratorio datos`, esperar 6 s, lote nuevo, revisar reloj |

## Consultas SQL de verificación

En el SQL analytics endpoint del lakehouse indicado (tablas bajo `dbo`). Pulsar **Refresh** si una tabla no aparece.

```sql
-- lh_silver · estado de lotes por fuente (crm.clientes_crm o devoluciones.lineas_devolucion)
SELECT batch_id, estado, modo, desde, hasta, version_contrato
FROM dbo.fwk_lotes
WHERE fuente = 'crm.clientes_crm'
ORDER BY observado_en;

-- lh_silver · ejecuciones de un lote (repetición: silver y gold en 'reutilizado'; Q3: 'error' con su mensaje)
SELECT batch_id, capa, filas_leidas, filas_escritas, filas_rechazadas, estado, mensaje
FROM dbo.fwk_ejecuciones
WHERE batch_id LIKE 'crm-inc%'
ORDER BY inicio;

-- lh_silver · cuarentena por lote de observación y versión de contrato
-- Tras Q2: dev-q1 con 10 (v1) y 39 (v2). Tras Q4: además 39 en v4.
SELECT batch_id, version_contrato, COUNT(*) AS rechazos
FROM dbo.fwk_cuarentena
GROUP BY batch_id, version_contrato;

-- lh_gold · historia de C0001 (tras la demo 5: Barcelona, Valencia, Barcelona)
SELECT id_cliente, ciudad, id_version, vigente_desde, vigente_hasta, es_actual
FROM dbo.dim_cliente
WHERE id_cliente = 'C0001'
ORDER BY vigente_desde;

-- lh_gold · ningún cliente con más de una versión vigente: no debe devolver filas
SELECT id_cliente, COUNT(*) AS actuales
FROM dbo.dim_cliente
WHERE es_actual = 1
GROUP BY id_cliente
HAVING COUNT(*) <> 1;

-- lh_gold · multiplicación de filas: 102 (con AND h.es_actual = 1, 100)
SELECT COUNT(*) AS filas
FROM dbo.dim_cliente_actual AS a
INNER JOIN dbo.dim_cliente AS h ON a.id_cliente = h.id_cliente;
```

## Cifras esperadas

| Momento | Resultado |
|---|---|
| Demo 2 · `crm-base` | 100 observaciones, 100 clientes, 100 filas en `dim_cliente`; `C0001` en Sevilla |
| Demo 3 · Q1 `dev-q1` | 397 leídas, 387 válidas, 10 rechazadas |
| Demo 3 · Q2 `dev-q2` | 358 válidas, 39 rechazadas |
| Demo 3 · Q3 `dev-q3` | Error «39 filas incumplen el contrato; no se publica»; lote en `revalidacion`; silver en 358 |
| Demo 3 · Q4 `dev-q3` | Confirmado con contrato 4; 358 válidas, 39 rechazadas |
| Demo 4 · `crm-inc-1` / `crm-inc-2` | 1 fila, `C0001` en Barcelona / 0 filas; 100 clientes |
| Demo 5 · tras `crm-scd2-a` | 102 versiones, 100 vigentes; `C0001` Barcelona → Valencia → Barcelona |
| Restauración (no ensayada) | Cuarta versión de `C0001` en Sevilla; 362 válidas y 35 rechazos |
