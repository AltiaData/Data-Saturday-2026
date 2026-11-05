# Demo 4 · De carga completa a incremental

Minutos 130–160 (30 min), tras el descanso. Guía del alumnado: [Demo 4](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-04`.

## Objetivo y mensajes clave

- Marca confirmada, límite superior fijo, estabilización y solape de cinco segundos.
- Extracción (completa o incremental) y escritura (`merge`) son decisiones independientes: CRM pasa a incremental y
  sigue escribiendo con `merge`.
- En CSV se lee el fichero completo y se filtra: no es pushdown, ni CDC, ni ahorro de I/O.
- Límites honestos: no se detectan borrados físicos ni cambios intermedios entre dos lecturas. Devoluciones sigue en
  completa porque no tiene una marca de modificación fiable.

## Qué enseñar en pantalla

- El diff del checkpoint, de una sola línea: `git diff -- config/fuentes/crm.yml` (`modo: completa` → `incremental`;
  `solape_segundos: 5` y `estabilizacion_segundos: 5` ya estaban). Entre ramas:
  `git diff alumno-99/demo-04 alumno-99/demo-05 -- config`.
- En el endpoint de `lh_silver`: `fwk_lotes` con `desde` y `hasta` de cada ventana y `fwk_ejecuciones` con la
  repetición en estado `reutilizado`.

## Comandos

```powershell
& $Python -m scripts.laboratorio checkpoint --paso incremental --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.modificar_csv ciudad --valor Barcelona
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

Fabric:

1. Bronze → silver → gold CRM con `batch_id="crm-inc-1"`.
2. Repetir `crm-inc-1`.
3. Esperar al menos 11 segundos y ejecutar `crm-inc-2` sin modificar el CSV.

```sql
SELECT batch_id, estado, modo, desde, hasta FROM dbo.fwk_lotes WHERE fuente = 'crm.clientes_crm' ORDER BY observado_en;
SELECT batch_id, capa, filas_leidas, filas_escritas, estado FROM dbo.fwk_ejecuciones
WHERE batch_id LIKE 'crm-inc%' ORDER BY inicio;
```

## Resultado esperado

- `crm-inc-1`: ventana desde la marca menos 5 s; una fila en bronze y silver; silver y gold con 100 clientes;
  `C0001` en Barcelona sin historia (tipo1); marca avanzada.
- Repetición de `crm-inc-1`: sin duplicados ni cambio de marca; silver y gold en `reutilizado`.
- `crm-inc-2`: cero filas extraídas; silver con 100; la marca puede avanzar.
- `desde` de cada ventana empieza cinco segundos antes del `hasta` anterior.

## Tiempo medido

9 ejecuciones, unos 22 min, con tres reintentos por 430. `crm-inc-1`: 110 s, 227 s (con un 430) y 110 s; repetición,
unos 92 s por notebook; `crm-inc-2` con dos reintentos. Margen **justo** para 30 minutos.

## Preguntas frecuentes previsibles

- **¿Esto ahorra lectura?** No con CSV: se lee el fichero entero y se filtra. El ahorro físico requeriría pushdown en un
  origen que lo admita.
- **¿Para qué el solape de 5 s?** Para no perder filas con marca cercana al límite; la escritura `merge` absorbe lo que
  se lea dos veces.
- **¿Por qué esperar 6 y 11 segundos?** Por la estabilización: una marca demasiado reciente se deja para la siguiente
  ventana.
- **¿Se detecta un borrado en origen?** No. Tampoco un valor que cambie dos veces entre lecturas.
- **¿Por qué devoluciones no pasa a incremental?** No dispone de una marca de modificación fiable.

## Incidencias reales del diario

- Hallazgo 25 (corregido): la guía no explicaba cómo comprobar ventana, solape y repetición; ahora incluye las
  consultas de arriba.
- Hallazgo 26 (pendiente): `data/README.md` dice que un reintento «reutiliza bronze y no vuelve a leer el CSV», pero en
  el ensayo bronze registró `ok` con una fila leída (sin duplicar) y solo silver y gold aparecieron `reutilizado`. Si
  alguien lo pregunta, lo que vale es lo observado.
- Hallazgo 27: la demo consume unos 25 min de cómputo de los 30; recorte pendiente de decisión.
- Riesgo documentado en la guía: un reloj local adelantado respecto a Fabric deja una marca futura fuera de la ventana
  hasta que llegue su momento.

## Plan B

Procedimiento común en el [README](README.md#plan-b-común-incorporarse-en-la-demo-nn). Lote previo: `crm-base`
(3 ejecuciones), en extracción completa, que es la configuración de la rama `demo-04`.

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-04
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
if (-not (Test-Path data/laboratorio)) { & $Python -m scripts.modificar_csv preparar }
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

Fabric: bronze → silver → gold CRM con `batch_id="crm-base"`. Después, la demo desde `checkpoint --paso incremental`.
No ejecutar `crm-base` en incremental: un incremental sin baseline no tiene marca de la que partir.
