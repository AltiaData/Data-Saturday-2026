# Demo 2 · Carga completa y dimensión tipo1

Minutos 50–75 (25 min). Guía del alumnado: [Demo 2](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-02`.

## Objetivo y mensajes clave

- Clave de negocio y tipos contractuales: el contrato silver manda sobre lo que llega del origen.
- Una observación (lo que se leyó en un lote) no es lo mismo que una actualización del origen.
- La baseline establece una marca confirmada, que más adelante usará el incremental.
- `merge` evita duplicar claves; bronze conserva cada lote.
- Un lote es el mismo identificador en bronze, silver y gold. Reintentar es repetir el identificador original.

## Qué enseñar en pantalla

- `config/fuentes/crm.yml`: `columna_marca: fecha_cambio`, `extraccion.modo: completa`, `modo_carga: merge`.
- `contracts/silver/clientes_crm.yml` y `config/modelos/dim_cliente.yml` (`tipo: tipo1`).
- La celda de parámetros de un notebook: solo se cambian parámetros, nunca lógica ni imports.
- Tras cargar, en el endpoint de `lh_silver`: `fwk_lotes`, `fwk_marcas` y `fwk_ejecuciones`.

## Comandos

En Fabric, con **Run all** y una sesión cada vez (Stop session entre notebooks). Parámetros comunes:
`entorno="dev"`, `workspace_datos="<workspace datos propio>"`, `dominio="crm"`, `fuente="clientes_crm"`.

1. `nb_10_bronze_ingesta` → `nb_20_silver_estandarizar` → `nb_30_gold_dimension` (`modelo="dim_cliente"`) con
   `batch_id="crm-base"`.
2. Repetir los tres con `crm-base` (idempotencia).

No cargar devoluciones todavía: la demo 3 siembra los defectos antes de su primer lote.

## Resultado esperado

- 100 observaciones en bronze, 100 clientes en silver y 100 filas en `dim_cliente`; `C0001` en Sevilla.
- `fwk_lotes` con `crm-base` confirmado (completa, contrato 1) y marca UTC registrada en `fwk_marcas`.
- Tras la repetición: 100 filas y 100 claves en las tres capas, un único lote y la misma marca; `fwk_ejecuciones`
  registra seis ejecuciones.

## Tiempo medido

6 ejecuciones, unos 16 min, con dos reintentos por error 430. Primera pasada: bronze 112 s, silver 115 s, gold 107 s
(tras un 430). Repetición: bronze 88 s; silver y gold con un reintento cada uno. Margen **justo** para 25 minutos.

## Preguntas frecuentes previsibles

- **¿Por qué no se duplica nada al repetir?** Silver y gold escriben con `merge` por clave y el lote ya está
  confirmado; bronze conserva el lote sin duplicarlo.
- **¿Qué guarda la marca?** El límite superior confirmado de `fecha_cambio` en UTC; el incremental de la demo 4 parte
  de ella.
- **¿Por qué tarda tanto un notebook con 100 filas?** Casi todo el tiempo es el arranque de la sesión de Spark.
- **¿Puedo lanzar los tres notebooks a la vez?** No en una capacidad pequeña: solo cabe una sesión.

## Incidencias reales del diario

- Hallazgo 17: en Trial FTL4, cada notebook lanzado justo después de otro falla con `TooManyRequestsForCapacity` (430).
  La sesión interactiva sigue viva tras ejecutar: **Stop session**, esperar un minuto y reintentar.
- Hallazgo 18: los SQL endpoints no mostraban ninguna tabla minutos después de cargar; aparecieron al pulsar
  **Refresh**. No interpretarlo como fallo de carga.
- Hallazgo 16: las tablas quedan en `Tables/` sin subcarpeta `dbo`; en el endpoint aparecen bajo `dbo`.
- Hallazgo 19: la demo consume 12–20 min de sus 25; el recorte está pendiente de decisión (véase la
  [chuleta](00_chuleta-del-dia.md#si-se-va-con-retraso-opciones-decisión-pendiente)).

## Plan B

Procedimiento común en el [README](README.md#plan-b-común-incorporarse-en-la-demo-nn).

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-02
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
if (-not (Test-Path data/laboratorio)) { & $Python -m scripts.modificar_csv preparar }
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

Requiere la publicación de la demo 1 (lakehouses, wheel, notebooks vinculados). Lotes previos en Fabric: ninguno.
CSV: el de `preparar`, sin mutaciones.
