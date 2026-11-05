# Manual del profesorado · Data Saturday 2026

Manual para impartir el workshop de cuatro horas del viernes 6 de noviembre de 2026. Complementa, sin sustituirla,
la guía que sigue el alumnado ([Seguir las demos](../workshop/02_seguir-las-demos.md)): aquí está lo que el
profesorado necesita además de los comandos, es decir, qué contar, qué enseñar, qué falló en el ensayo y cómo
reincorporar a quien se retrase.

Todo lo que se afirma sobre resultados, tiempos e incidencias procede del ensayo completo de las siete demos que se hizo
el 4 y 5 de noviembre de 2026 como `alumno-99` (Trial FTL4 en West Europe, Runtime 1.3 con Spark 3.5, `datafwk` 0.3.0,
proyecto `fsh-alumno99`) y está registrado en el [diario del ensayo](../workshop/ensayo-alumno-99.md). Lo que no se
ensayó se indica como tal.

## Índice

| Fichero | Contenido | Minutos del plan |
|---|---|---|
| [00 · Chuleta del día](00_chuleta-del-dia.md) | Comprobaciones previas, tiempos, recortes y consultas SQL en una página | — |
| [01 · Greenfield](01_greenfield.md) | Generar el proyecto y publicar recursos | 15–50 |
| [02 · Completa y tipo1](02_completa-tipo1.md) | Baseline CRM, marca e idempotencia | 50–75 |
| [03 · Calidad y cuarentena](03_calidad-cuarentena.md) | Defectos de origen y contratos Q1 → Q4 | 75–115 |
| [04 · Incremental](04_incremental.md) | Completa → incremental, ventana y solape | 130–160 |
| [05 · SCD2](05_scd2.md) | Ciudad de tipo1 a SCD2, cambio de grano | 160–200 |
| [06 · Consumo y Cosmos](06_consumo-cosmos.md) | Proyección vigente, multiplicación de filas y volcado Cosmos | 200–220 |
| [07 · Revisión](07_revision.md) | Catálogo, linters, tests y secretos fuera de Git | 220–235 |
| [08 · Restauración y cierre](08_restauracion-y-cierre.md) | Restaurar el origen sin perder historia | 235–240 |

Los minutos 0–15 (arquitectura y reglas) y el descanso (115–130) no tienen capítulo propio: su contenido está en
[la guía del alumnado](../workshop/02_seguir-las-demos.md) (sección «Arquitectura y reglas») y en
[el plan](../workshop/02_plan-sesion-4-horas.md).

Cada capítulo de demo tiene la misma estructura: objetivo y mensajes clave · qué enseñar en pantalla · comandos ·
resultado esperado · tiempo medido · preguntas frecuentes previsibles · incidencias reales del diario · plan B.

## Fuentes

El manual resume y ordena estas fuentes de la rama `alumno-99/setup`; si hay discrepancia, mandan ellas:

- [02_seguir-las-demos.md](../workshop/02_seguir-las-demos.md): comandos, parámetros y resultados esperados.
- [02_plan-sesion-4-horas.md](../workshop/02_plan-sesion-4-horas.md): plan de 240 minutos y tabla de tiempos medidos.
- [01_preparacion-instructores.md](../workshop/01_preparacion-instructores.md) y
  [01_antes-de-la-sesion.md](../workshop/01_antes-de-la-sesion.md): preparación del profesorado y del alumnado.
- [ensayo-alumno-99.md](../workshop/ensayo-alumno-99.md): 36 hallazgos y registro de incidencias reales.
- [infra/lab/README.md](../../infra/lab/README.md): script de creación de workspaces y `env_fwk`.

## Flujo de ramas

```text
  main (no se toca)
    |
    v
  alumno-99/setup  (correcciones comunes + diario del ensayo)
    |
    |-- merge --> alumno-99/demo-01            plantilla: punto inicial de la demo 1
    |-- merge --> alumno-99/demo-02 ... 07     proyecto generado: punto inicial de cada demo
    |
    '-- merge --> profesor                     este manual

  Sentido único: profesor  --X-->  alumno-99/setup        (nunca)
                 profesor  --X-->  alumno-99/demo-NN      (nunca)
```

- `alumno-99/setup` recibe las correcciones comunes y el diario. Después se fusiona en cada `alumno-99/demo-NN`.
- `alumno-99/demo-NN` es el estado del repositorio al **empezar** la demo NN. `demo-01` es la plantilla; desde
  `demo-02` contiene el proyecto que genera `crear_proyecto.py` (con los nombres de `fsh-alumno99`), con los
  checkpoints de las demos anteriores ya aplicados.
- `profesor` nace de `alumno-99/setup` y solo recibe fusiones desde `setup`. **Nunca** se fusiona hacia `setup` ni hacia
  las ramas de demo: así el manual no llega a los puntos iniciales que usa el alumnado.
- `main` no se toca. El alumnado puede ver la rama `profesor`; no hace falta ocultarla.

Para actualizar el manual con correcciones posteriores de `setup`:

```powershell
git switch profesor
git merge alumno-99/setup
```

### Qué contiene cada rama de demo

Comprobado con `git show` sobre cada rama:

| Rama | Contrato `lineas_devolucion` | Extracción CRM | Modelo `dim_cliente` | `dim_cliente_actual` |
|---|---|---|---|---|
| `demo-02`, `demo-03` | `version: 1` | `completa` | `tipo1` | No |
| `demo-04` | `version: 4` | `completa` | `tipo1` | No |
| `demo-05` | `version: 4` | `incremental` | `tipo1` | No |
| `demo-06`, `demo-07` | `version: 4` | `incremental` | `scd2` | Sí |

Las ramas versionan **solo el repositorio**. El estado de Fabric (tablas Delta, lotes, marcas, historia) y los CSV de
trabajo de `data/laboratorio/` (ignorados por Git) no viajan con `git switch`. Por eso cada plan B dice también qué
CSV preparar y qué lotes ejecutar.

## Plan B común: incorporarse en la demo NN

Para quien se retrase o rompa su laboratorio. **Procedimiento derivado de las fuentes y del código de
`scripts/laboratorio.py`; no se ensayó con otro tenant.** En el ensayo, desde la demo 3, sí se trabajó sobre la copia
de trabajo de cada rama en lugar de sobre el proyecto generado.

1. En la copia del repositorio entregada (`$Plantilla`, donde ya está `.env.alumno`), con el árbol limpio:

   ```powershell
   Set-Location $Plantilla
   git switch alumno-99/demo-NN
   & $Python -m scripts.laboratorio configurar --env-file .env.alumno
   ```

   `configurar` reescribe `config/entornos/dev.yml` y `fabric/ingenieria/parameter.yml` con los nombres de los
   workspaces propios en lugar de los de `fsh-alumno99`. Esos dos ficheros quedan modificados: no se hace commit. Si
   un `git switch` posterior se niega por cambios locales,
   `git restore config/entornos/dev.yml fabric/ingenieria/parameter.yml`, cambiar de rama y repetir `configurar`.
2. Si nunca se publicó nada en Fabric (demo 1 sin terminar), publicar como en la demo 1: `lakehouses`, `build`,
   `wheel`, `notebooks`, y vincular los cinco notebooks a `env_fwk`. Si ya se publicaron los notebooks del greenfield
   propio, no es necesario volver a publicarlos: la celda de parámetros se cambia en cada ejecución.
3. CSV de trabajo: si no existe `data/laboratorio/`, `& $Python -m scripts.modificar_csv preparar`. Aplicar las
   mutaciones que indique el capítulo y publicar con `laboratorio config` y `laboratorio datos`.
4. Ejecutar en Fabric los lotes previos que indique el capítulo, **cada uno con la configuración de la rama en la que
   se ejecutó durante el ensayo** (por ejemplo, `crm-base` en extracción completa, aunque la demo de destino ya sea
   incremental). Las repeticiones de idempotencia no hacen falta para ponerse al día.

Resumen (los lotes previos proceden del diario; cada notebook tardó entre 90 y 135 s en el ensayo):

| Demo de destino | Lotes previos en Fabric | Ejecuciones de notebook |
|---|---|---:|
| 1, 2, 3 | Ninguno | 0 |
| 4 | `crm-base` | 3 |
| 5 | `crm-base`, `crm-inc-1`, `crm-inc-2` | 9 |
| 6 | Los anteriores, `crm-activar`, `crm-scd2-b`, `crm-scd2-a` | 18 |
| 7 | Ninguno (solo repositorio) | 0 |

Ponerse al día para las demos 5 y 6 cuesta más que la propia demo en una capacidad pequeña: en esos casos es más
realista que la persona siga la demo en la pantalla del profesorado y haga las partes locales.

## Cómo usar el manual el día del taller

1. La víspera y una hora antes: [chuleta](00_chuleta-del-dia.md), sección de comprobación previa.
2. Proyectar la guía del alumnado; tener el capítulo de la demo en curso en una segunda pantalla o impreso.
3. Al empezar cada demo, leer «Objetivo y mensajes clave» y abrir lo indicado en «Qué enseñar en pantalla» antes de
   que el alumnado lance notebooks: en capacidades pequeñas cada ejecución tarda 1,5–2 minutos y la explicación
   puede solaparse con la espera.
4. Ante un error, mirar primero «Incidencias reales del diario» del capítulo y la tabla de incidencias de la chuleta.
5. Llevar la cuenta del retraso contra la tabla de tiempos de la chuleta y aplicar el recorte que se haya decidido
   (véase «Pendiente»).

El laboratorio de Fabric de `alumno-99` queda como está tras el ensayo (sin restaurar) y sirve de referencia para
enseñar resultados. Para la demostración en directo hace falta otro producto y workspaces vacíos
([preparación, punto 3.7](../workshop/01_preparacion-instructores.md#3-preparar-tu-ensayo-y-la-entrega-a-alumnos)).

## Pendiente (fuera de este manual)

- **Recortes de tiempo.** Las demos 2, 4 y 5 y la restauración no tienen margen con una capacidad pequeña. La chuleta
  propone opciones; la decisión está pendiente.
- **Etiquetas `demo-NN-inicio`** al congelar el material: etiquetar el punto inicial de cada rama de demo.
- **Hallazgos pendientes del diario:** 1 (`templates/workshop/README.md` describe la edición SQL), 15 (publicar el
  wheel en la preparación previa), 19, 27 y 30 (recortes de las demos 2, 4 y 5), 26 (frase de reintento de
  `data/README.md`) y 36 (actualizar `03_validacion-edicion.md`).
