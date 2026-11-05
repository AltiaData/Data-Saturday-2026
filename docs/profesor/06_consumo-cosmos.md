# Demo 6 · Consumo y documentos Cosmos

Minutos 200–220 (20 min). Guía del alumnado: [Demo 6](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-06`.

## Objetivo y mensajes clave

- Una dimensión vigente se relaciona por `id_cliente`; relacionar hechos con el histórico por esa clave multiplica
  filas.
- Una unión temporal necesita la fecha del hecho y una definición de negocio acordada. **No se crean KPIs que no estén
  definidos** en el glosario o en un contrato.
- El volcado Cosmos conserva los documentos completos en `documento_json`, sin perder arrays, objetos ni IDs.
- Una fuente Cosmos nueva necesita proyección y contrato antes de entrar en el pipeline: no se promete un silver Cosmos
  sin sus contratos.

## Qué enseñar en pantalla

- En el endpoint de `lh_gold`: la consulta de multiplicación (102 filas frente a 100) y su corrección con
  `es_actual = 1`. Las devoluciones no tienen `id_cliente`, por eso se usa la proyección vigente en lugar de un hecho.
- `data/original/manifest.json`: los diez contenedores Cosmos y sus `partition_key_paths`.
- Una parte CSV de Cosmos abierta con un lector CSV, o el ejemplo de lectura de `data/README.md`.

## Comandos

```sql
SELECT COUNT(*) FROM dbo.dim_cliente_actual;

SELECT COUNT(*) AS filas
FROM dbo.dim_cliente_actual AS a
INNER JOIN dbo.dim_cliente AS h ON a.id_cliente = h.id_cliente;
```

Repetir la segunda con `AND h.es_actual = 1` en la condición.

```powershell
& $Python -m scripts.modificar_csv verificar
```

## Resultado esperado

- `dim_cliente_actual` con 100 filas; `dim_cliente` con 102; `C0001` con tres filas.
- La unión con el histórico devuelve 102 filas y `C0001` aparece tres veces; con `es_actual = 1`, 100.
- Manifiesto con diez contenedores y su clave de partición; `verificar` indica un volcado íntegro.
- El ejemplo corregido de `data/README.md` acumula todas las partes: 9.050 documentos en `eventos_web`.

## Tiempo medido

Sin notebooks; unos 5 min de consultas y comprobaciones locales. Margen **holgado**: sirve para recuperar retraso de
la demo 5 o para conversación.

## Preguntas frecuentes previsibles

- **¿Cómo uno una venta con la ciudad que tenía el cliente en su fecha?** Con una unión temporal por `vigente_desde` y
  `vigente_hasta`, pero exige la fecha del hecho y una definición de negocio acordada: si no está en el glosario, se
  pregunta, no se inventa.
- **¿Por qué no se carga Cosmos en silver?** No hay contratos para esas fuentes; antes harían falta proyección y
  contrato.
- **¿El volcado de SQL y Cosmos es coherente entre sí?** Es una extracción secuencial del 2 de noviembre de 2026, no un
  snapshot transaccional entre servicios.

## Incidencias reales del diario

- Hallazgo 31 (corregido): el ejemplo de lectura Cosmos de `data/README.md` reasignaba la lista en cada parte y solo
  quedaban los documentos de la última. Quien traiga una copia antigua verá un total menor.
- Hallazgo 32 (corregido): la multiplicación de filas solo se explicaba; ahora hay una consulta que la muestra.
- Si alguna tabla no aparece en el endpoint de `lh_gold`, pulsar **Refresh** (hallazgo 18).

## Plan B

Procedimiento común en el [README](README.md#plan-b-común-incorporarse-en-la-demo-nn). Para las consultas de gold hacen
falta todos los lotes CRM anteriores: `crm-base`, `crm-inc-1`, `crm-inc-2`, `crm-activar`, `crm-scd2-b`, `crm-scd2-a`
(18 ejecuciones). No cabe en el bloque: lo realista es mostrar las consultas en la pantalla del profesorado.

La parte de Cosmos (pasos 3 a 5 de la guía) es local y no necesita Fabric:

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-06
& $Python -m scripts.modificar_csv verificar
```

Si se quiere reconstruir el estado completo fuera del taller: seguir el plan B de la [demo 5](05_scd2.md#plan-b) y
después, con la rama `demo-06` (`configurar` y `config`), ejecutar `crm-activar` (bronze, silver y
`nb_90_ops_activar_scd2`), `ciudad --valor Valencia` con `crm-scd2-b` y `ciudad --valor Barcelona` con `crm-scd2-a`,
publicando los datos y esperando 6 s tras cada cambio de CSV.
