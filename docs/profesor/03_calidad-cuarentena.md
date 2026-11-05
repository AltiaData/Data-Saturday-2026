# Demo 3 · Errores de origen y evolución de la cuarentena

Minutos 75–115 (40 min). Guía del alumnado: [Demo 3](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-03`.

## Objetivo y mensajes clave

- Distinguir un dato inválido de una regla que cambia.
- La evidencia de cuarentena se guarda por versión de contrato; su total acumulado no es el número de rechazos
  pendientes.
- Revalidar reconstruye silver desde bronze con el contrato vigente, sin leer el CSV ni avanzar la marca.
- Política `cuarentena` frente a `fallar`, y recuperación de un lote pendiente repitiendo **el mismo** lote.
- Reglas ya pactadas en los contratos: reembolso no negativo y no nulo; desde Q2, motivo no nulo. Una cadena vacía no
  equivale automáticamente a NULL.
- El cambio de contrato Q1 → Q2 → Q3 → Q4 es un cambio para quien consume la tabla: anunciarlo en cada paso.

## Qué enseñar en pantalla

- Tras cada `checkpoint`: `git diff -- contracts/silver/lineas_devolucion.yml`. Diff Q1 → Q4 completo entre ramas:
  `git diff alumno-99/demo-03 alumno-99/demo-04 -- contracts` (`motivo.nulo: true` → `false`, `version: 1` → `4`).
- El contrato Q3: `version: 3` con política `fallar`.
- La salida del notebook de revalidación Q3, donde aparece el mensaje de contrato (la API de jobs solo da un error
  genérico).
- En el endpoint de `lh_silver`: `fwk_cuarentena` agrupada por `batch_id` y `version_contrato`, y `fwk_lotes`.

## Comandos

```powershell
& $Python -m scripts.modificar_csv defectos
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

Fabric: bronze → silver devoluciones (`dominio="devoluciones"`, `fuente="lineas_devolucion"`) con `batch_id="dev-q1"`.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso calidad --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
git diff -- contracts/silver/lineas_devolucion.yml
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Fabric: `nb_90_ops_revalidar` con `batch_id="dev-q2"`; repetir `dev-q2`.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso fallar --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Fabric: revalidación con `batch_id="dev-q3"` (debe fallar).

```powershell
& $Python -m scripts.laboratorio checkpoint --paso recuperar --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Fabric: revalidación con **el mismo** `batch_id="dev-q3"`.

## Resultado esperado

| Paso | Resultado |
|---|---|
| Q1 `dev-q1` | 397 leídas, **387 válidas y 10 rechazadas** (ya había ocho rechazos Q1 antes de sembrar defectos) |
| Q2 `dev-q2` | **358 válidas y 39 rechazadas**, incluidas filas aceptadas con Q1; marca sin cambios |
| Repetición `dev-q2` | Sin evidencia duplicada |
| Q3 `dev-q3` | Error «`lineas_devolucion: 39 filas incumplen el contrato; no se publica`»; silver sigue en 358; cuarentena y marca sin cambios; `fwk_ejecuciones` con una ejecución `error`; `fwk_lotes` con `dev-q3` en `revalidacion` |
| Q4 `dev-q3` | Confirmado con contrato 4; 358 válidas y 39 rechazos de la versión 4 |

Cuarentena tras Q2: `dev-q1` con 10 rechazos en la versión 1 y 39 en la versión 2. Filtrar por `batch_id = 'dev-q2'`
devuelve cero filas: la evidencia conserva el lote en que se **observó** cada fila.

## Tiempo medido

6 ejecuciones, unos 11 min: `dev-q1` bronze 105 s y silver 121 s; Q2 123 s; repetición 87 s; Q3 108 s; Q4 115 s.
Margen **holgado**: es la demo con más tiempo para la explicación.

## Preguntas frecuentes previsibles

- **¿Por qué 10 rechazos si solo se sembraron cuatro defectos?** Con este volcado ya había ocho rechazos Q1; dos de los
  cuatro defectos son motivos NULL, que Q1 aún admite.
- **¿Por qué filtrar por `dev-q2` no devuelve nada?** La evidencia lleva el lote de observación (`dev-q1`), no el de
  revalidación.
- **¿Q3 rompe silver?** No: falla antes de publicar; silver, cuarentena y marca no cambian.
- **¿Por qué no lanzar un lote nuevo para salir de Q3?** El lote pendiente se recupera cambiando explícitamente el
  contrato y repitiendo ese mismo lote; no se salta.
- **¿Q4 vuelve a Q1?** No: mantiene el motivo obligatorio y recupera la política de cuarentena.

## Incidencias reales del diario

- Hallazgo 20: la consulta por `dev-q2` devuelve cero filas; usar la agrupación por versión de contrato.
- Hallazgo 21: el estado del lote fallido es `revalidacion` y el mensaje de contrato solo está en la salida del
  notebook y en `fwk_ejecuciones`.
- Hallazgo 22 (corregido): sin `validar_contratos` y `generar_catalogo` tras cada checkpoint, el hook
  `catalogo-actualizado` falla en la demo 7.
- Hallazgos 23 y 24 (corregidos): YAML generado que incumplía `yamllint` y descripciones de contratos con texto de la
  edición SQL.

## Plan B

Procedimiento común en el [README](README.md#plan-b-común-incorporarse-en-la-demo-nn). La demo 3 es independiente de
CRM: no necesita lotes previos.

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-03
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
if (-not (Test-Path data/laboratorio)) { & $Python -m scripts.modificar_csv preparar }
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Después, la demo desde `modificar_csv defectos`. Si la persona se incorpora a mitad de la demo, no hay atajo: los
pasos Q2 a Q4 dependen de `dev-q1` y de los anteriores, y son una ejecución cada uno.
