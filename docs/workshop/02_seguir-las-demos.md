# Seguir las demos · Cuaderno del alumno

Duración: 240 minutos, incluido descanso de 15 minutos. Preparación previa: [antes de la sesión](01_antes-de-la-sesion.md).
Anota tus resultados en la [ficha](00_ficha-laboratorio.md).

**LOCAL:** ejecutar en tu producto generado. **FABRIC:** solo en tu laboratorio individual asignado;
en modalidad guiada observar la ejecución del instructor. **SQL:** coordinar con el instructor, siempre en la copia dedicada.

## Agenda

| Minutos | Actividad |
|---|---|
| 00–10 | Objetivo y evidencias |
| 10–30 | Contexto, contratos y arquitectura |
| 30–65 | 1. Greenfield |
| 65–90 | 2. Completa y calidad Q1 |
| 90–115 | 3. Q2, fallo Q3 y recuperación Q4 |
| 115–130 | Descanso |
| 130–160 | 4. Completa → incremental |
| 160–200 | 5. Ciudad tipo1 → SCD2 |
| 200–220 | 6. Consumo actual e histórico |
| 220–235 | 7. Revisión y pruebas |
| 235–240 | Cierre |

## Contexto · 00–30

Abre `AGENTS.md`, `docs/convenciones.md`, `docs/glosario.md` y un notebook en `fabric/ingenieria/`.
Localiza la función de biblioteca que invoca. Explica dónde declararías:

- Cuánto leer del origen: `fuentes.extraccion`.
- Cómo escribir silver: `modo_carga`.
- Qué aceptar: contrato.
- Qué atributos guardar con historia: `modelos.historificacion`.

No son cuatro nombres para la misma decisión. Los notebooks orquestan; la lógica vive en `src/datafwk/`.

## Demo 1 · Proyecto greenfield · 30–65

### Paso 1. Generar desde esta plantilla

**LOCAL, desde la raíz de la copia de alumnos.** La virtualenv se preparó antes de la sesión.

~~~powershell
$Plantilla = (Get-Location).Path
$PythonPlantilla = Join-Path $Plantilla '.venv\Scripts\python.exe'
$NombreProyecto = 'fsh-equipo01'
$Proyecto = Join-Path (Split-Path -Parent $Plantilla) $NombreProyecto

if (Test-Path -LiteralPath $Proyecto) {
    throw 'Elige una carpeta nueva; no borres un proyecto para repetir la demo'
}

& $PythonPlantilla "$Plantilla\scripts\crear_proyecto.py" $Proyecto --proyecto $NombreProyecto
Set-Location -LiteralPath $Proyecto
git init -b main
git add --all
git commit -m "Crea proyecto desde datafwk 0.2.0"
git switch -c feat/workshop
~~~

Cambiar `fsh-equipo01` por tu nombre asignado antes de ejecutar.
**Esperado:** proyecto independiente, ocho IDs Fabric renovados y checkpoints todavía sin activar.
La documentación se copia también; no vuelvas a generar un proyecto desde dentro del producto siguiendo este mismo paso.

### Paso 2. Entorno del producto y contratos iniciales

~~~powershell
& $PythonPlantilla -m venv .venv
$Python = Join-Path $Proyecto '.venv\Scripts\python.exe'
$env:PATH = "$Proyecto\.venv\Scripts;$env:PATH"
$env:PYSPARK_PYTHON = $Python
& $Python -m pip install -e '.[dev,deploy]'

Copy-Item .\templates\workshop\01_base\contracts\* .\contracts -Recurse -Force
Copy-Item .\templates\workshop\01_base\config\* .\config -Recurse -Force
~~~

Usar la caché/entorno preparado; no resolver instalaciones largas durante el bloque.
En `config/entornos/dev.yml` conservar el nombre de workspace generado y añadir `conexiones_sql`.
Para revisión exclusivamente local este ejemplo es deliberadamente no conectable:

~~~yaml
nombre: dev
workspace_datos: fsh-equipo01-datos-dev
lakehouses:
  bronze: lh_bronze
  silver: lh_silver
  gold: lh_gold
ruta_config: _framework
conexiones_sql:
  oltp_workshop:
    servidor: sql-laboratorio.example.invalid
    base: base_laboratorio
~~~

En laboratorio individual sustituir por valores reales de tu ficha; añadir `esquema: dbo` si corresponde.
No ejecutar conexión/publicación usando el ejemplo `.invalid`.

~~~powershell
& $Python scripts/agente_lint.py contracts/silver/clientes_crm.yml contracts/silver/lineas_devolucion.yml contracts/gold/dim_cliente.yml config/fuentes/crm.yml config/fuentes/devoluciones.yml config/modelos/dim_cliente.yml config/entornos/dev.yml
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
& $Python -m pytest tests/contracts/test_workshop.py tests/unit/test_crear_proyecto.py -q
git diff --stat
git add --all
git commit -m "Activa fuentes SQL y dimension tipo1"
~~~

**Esperado:** contratos de clientes/líneas, fuentes CRM/devoluciones y `dim_cliente` tipo1.
Una tabla nueva tiene contrato antes del código que la genera.

### Paso 3. Publicar (solo laboratorio individual)

El instructor debe haber preparado workspaces, lakehouses y `env_fwk` con wheel 0.2.0.
Pedir sus IDs si te corresponde publicar; no reutilizar los del entorno compartido.

~~~powershell
az login --tenant '<tenant-asignado>'
$env:WS_ING_ID = '<id-tu-workspace-ingenieria>'
& $Python scripts/publicar_config.py --entorno dev

@'
import os
from pathlib import Path
from azure.identity import AzureCliCredential
from fabric_cicd import FabricWorkspace, publish_all_items

workspace = FabricWorkspace(
    workspace_id=os.environ["WS_ING_ID"],
    environment="DEV",
    repository_directory=str(Path("fabric/ingenieria").resolve()),
    item_type_in_scope=["Notebook"],
    token_credential=AzureCliCredential(),
)
publish_all_items(workspace)
'@ | & $Python -
~~~

En Fabric asociar `env_fwk` a los cinco notebooks y arrancar sesión nueva.
La publicación se limita a notebooks para conservar el Environment preparado.
Si publica el instructor, entregarle tu configuración y esperar su confirmación antes de cargar.

**Pregunta:** ¿por qué editar un YAML local todavía no cambia lo que ejecuta Fabric?

## Demo 2 · Completa y Q1 · 65–90

### Paso 1. Identificar el lote y ejecutar CRM

~~~powershell
$Run = Get-Date -Format 'yyyyMMddHHmmss'
Write-Output $Run
~~~

En todas las tablas siguientes `<R>` es tu Run o el del instructor si observas la demo.
Parámetros comunes: `entorno=dev` y `workspace_datos=<el de tu ficha>`.

| Orden | Notebook | Parámetros |
|---|---|---|
| 1 | `nb_10_bronze_ingesta` | `dominio=crm`, `fuente=clientes_crm`, `batch_id=<R>-crm-01` |
| 2 | `nb_20_silver_estandarizar` | Mismos dominio, fuente y lote |
| 3 | `nb_30_gold_dimension` | Mismos parámetros, `modelo=dim_cliente` |

**Esperado:** una fila por cliente en silver y dimensión tipo1; marca CRM confirmada tras silver.
El límite superior excluye los últimos cinco segundos.

### Paso 2. Observar defectos SQL y cargar devoluciones

El instructor respalda cuatro líneas válidas y siembra: importe negativo, importe NULL y dos motivos NULL.
Conserva PK/FK/CHECK. Si tu laboratorio es individual, coordinar las mismas mutaciones en tu copia SQL.

| Orden | Notebook | Parámetros |
|---|---|---|
| 1 | `nb_10_bronze_ingesta` | `dominio=devoluciones`, `fuente=lineas_devolucion`, `batch_id=<R>-dev-q1` |
| 2 | `nb_20_silver_estandarizar` | Mismos parámetros |

Q1 exige importe no nulo/no negativo; permite motivo NULL.
**Esperado:** `N−R1` filas aceptadas y `R1` evidencias. En la muestra exacta de diez filas: 8 y 2.
No hay notebook gold de devoluciones que ejecutar.

### Paso 3. Inspeccionar

**FABRIC, sesión de inspección**, usando sus parámetros `entorno` y `workspace_datos`.
Los fragmentos de inspección se ejecutan de forma exploratoria; no pegarlos en los notebooks de carga.

~~~python
from pyspark.sql import functions as F
from datafwk import rutas
from datafwk.arranque import cargar_contexto
from datafwk.control import Control, leer_version, version

run_id = "<R>"
ctx_crm = cargar_contexto(entorno, workspace_datos, "crm")
ctx_dev = cargar_contexto(entorno, workspace_datos, "devoluciones")
control = Control(spark, ctx_crm.entorno)
ruta_dev = rutas.tabla(ctx_dev.entorno, "silver", "lineas_devolucion")
ruta_q = rutas.tabla(ctx_dev.entorno, "silver", "fwk_cuarentena")
print("Aceptadas:", leer_version(spark, ruta_dev).count())
display(leer_version(spark, ruta_q).limit(20))
print(control.marca("crm.clientes_crm"))
~~~

Repetir bronze/silver CRM con el mismo lote: bronze reutiliza datos y responde `ok`; silver devuelve `reutilizado`.
**Pregunta:** ¿una fila rechazada es lo mismo que una evidencia histórica de rechazo?

## Demo 3 · Cambiar cuarentena · 90–115

### Paso 1. Aplicar Q2

**LOCAL:**

~~~powershell
Copy-Item .\templates\workshop\02_calidad\contracts\silver\lineas_devolucion.yml .\contracts\silver\lineas_devolucion.yml -Force
git diff -- contracts/silver/lineas_devolucion.yml
& $Python scripts/agente_lint.py contracts/silver/lineas_devolucion.yml
~~~

**Solo individual:** publicar con `& $Python scripts/publicar_config.py --entorno dev`.
En modo guiado el instructor publica su propia revisión.

**Cambio de contrato:** versión 2, `motivo.nulo: false`. Rechaza NULL, pero acepta vacío/espacios.

Guardar la marca antes y ejecutar `nb_90_ops_revalidar` con `devoluciones`, `lineas_devolucion`,
`batch_id=<R>-dev-q2`. No ejecutar bronze:

~~~python
marca_dev_antes = control.marca("devoluciones.lineas_devolucion")
~~~

**Esperado:** reconstruye silver desde todas las últimas observaciones bronze, incluidas las antes aceptadas.
`N−R2` aceptadas; muestra de diez: 6. La marca no cambia.

~~~python
assert control.marca("devoluciones.lineas_devolucion") == marca_dev_antes
display(leer_version(spark, ruta_q).groupBy("version_contrato", "batch_id").count().limit(20))
~~~

En la muestra hay 2 evidencias v1 + 4 v2. Su batch sigue siendo el bronze original `dev-q1`.
Repetir `dev-q2`: `reutilizado`, sin nuevas evidencias.

### Paso 2. Aplicar Q3 y observar el fallo esperado

~~~powershell
Copy-Item .\templates\workshop\03_fallar\contracts\silver\lineas_devolucion.yml .\contracts\silver\lineas_devolucion.yml -Force
& $Python scripts/agente_lint.py contracts/silver/lineas_devolucion.yml
~~~

Publicar en individual. Antes de ejecutar, guardar versiones:

~~~python
v_dev = version(spark, ruta_dev)
v_q = version(spark, ruta_q)
~~~

Ejecutar revalidación con `<R>-dev-q3`.
**Esperado:** `ContratoIncumplido`, auditoría `error`, lote pendiente `revalidacion`; silver/cuarentena sin cambios:

~~~python
assert version(spark, ruta_dev) == v_dev
assert version(spark, ruta_q) == v_q
assert control.marca("devoluciones.lineas_devolucion") == marca_dev_antes
~~~

### Paso 3. Recuperar con Q4, conservando dev-q3

~~~powershell
@'
from pathlib import Path
import yaml

p = Path("templates/workshop/02_calidad/contracts/silver/lineas_devolucion.yml")
c = yaml.safe_load(p.read_text(encoding="utf-8"))
c["version"] = 4
c["descripcion"] = "Revision Q4: condiciones Q2 y cuarentena para recuperar Q3."
Path("contracts/silver/lineas_devolucion.yml").write_text(
    yaml.safe_dump(c, allow_unicode=True, sort_keys=False), encoding="utf-8"
)
'@ | & $Python -
& $Python scripts/agente_lint.py contracts/silver/lineas_devolucion.yml
~~~

Publicar Q4 y reintentar **el mismo `<R>-dev-q3`**.
**Esperado:** confirmado con contrato 4, 6 aceptadas en la muestra y 4 evidencias nuevas.
No iniciar otro lote mientras Q3 siga pendiente. No volver silenciosamente a versión 2.

~~~powershell
git add contracts/silver/lineas_devolucion.yml docs/catalogo.md
git commit -m "Versiona calidad y recupera con Q4"
~~~

**Pregunta:** ¿por qué corregir SQL no corrige una observación bronze ya materializada?

## Descanso · 115–130

Quince minutos. El instructor confirma que Q3 se recuperó con Q4 antes de continuar.

## Demo 4 · Completa → incremental · 130–160

### Paso 1. Cambiar la extracción

~~~powershell
Copy-Item .\templates\workshop\04_incremental\config\fuentes\crm.yml .\config\fuentes\crm.yml -Force
git diff -- config/fuentes/crm.yml
& $Python scripts/agente_lint.py config/fuentes/crm.yml
~~~

Publicar solo en tu laboratorio individual.
**Esperado:** cambia `extraccion.modo`; `modo_carga: merge` y dimensión tipo1 permanecen.

En inspección, antes de la nueva carga:

~~~python
marca_crm_antes = control.marca("crm.clientes_crm")
assert marca_crm_antes is not None
~~~

### Paso 2. Cambio en origen y pausa tras bronze

El instructor cambia la ciudad del cliente a Barcelona **y updated_at**, en la copia SQL respaldada.
Esperar seis segundos. Ejecutar únicamente bronze CRM con `<R>-crm-02`.

~~~python
lote = control.lote("crm.clientes_crm", f"{run_id}-crm-02")
assert lote.estado == "bronze"
assert control.marca("crm.clientes_crm") == marca_crm_antes
print(lote.desde, lote.hasta)
~~~

Repetir bronze con ese ID y ejecutar silver/gold tipo1 con el mismo lote.
**Esperado:** ciudad Barcelona, una fila por cliente, marca igual a `lote.hasta`.

La pausa entre etapas es controlada; no se ha inyectado un error SQL.

### Paso 3. Solape y ventana vacía

Repetir silver/gold `crm-02`: `reutilizado`.
Esperar 12 segundos sin cambios SQL; ejecutar bronze→silver→gold `<R>-crm-03`.
Puede releer la última fila por el solape. Después de confirmarlo ejecutar `<R>-crm-04`.

**Esperado:** crm-04 vacío en bronze/silver si el origen sigue congelado. Gold lee la imagen silver completa;
sus contadores pueden incluir todos los clientes. La marca avanza también para una ventana vacía.

~~~powershell
git add config/fuentes/crm.yml
git commit -m "Cambia CRM a extraccion incremental"
~~~

**Pregunta:** ¿por qué esperar mucho antes de crm-03 no elimina por sí solo su solape?

## Demo 5 · Activar SCD2 en ciudad · 160–200

### Paso 1. Contratos antes que modelo

~~~powershell
Copy-Item .\templates\workshop\05_scd2\contracts\gold\* .\contracts\gold -Force
Copy-Item .\templates\workshop\05_scd2\config\modelos\dim_cliente.yml .\config\modelos\dim_cliente.yml -Force
git diff -- contracts/gold config/modelos
& $Python scripts/agente_lint.py contracts/gold/dim_cliente.yml contracts/gold/dim_cliente_actual.yml config/modelos/dim_cliente.yml
~~~

Publicar en individual.
**Cambio de contrato:** `dim_cliente` versión 2, grano por `id_version`. `id_cliente` ya no es único en el histórico.
`dim_cliente_actual` mantiene una fila por cliente.
El modelo declara `columnas: [ciudad]` dentro de historificación y `columnas_tipo1: []`.

### Paso 2. Activar con un nuevo lote

Congelar modificaciones SQL. Ejecutar bronze y silver CRM con `<R>-crm-scd0`.
Después ejecutar **nb_90_ops_activar_scd2**, con el mismo lote y `modelo=dim_cliente`.
No ejecutar primero el notebook gold ordinario para ese lote.

~~~python
from datafwk.scd2 import validar_historia

ctx_crm = cargar_contexto(entorno, workspace_datos, "crm")
modelo = ctx_crm.modelo("dim_cliente")
ruta_historia = rutas.tabla(ctx_crm.entorno, "gold", "dim_cliente")
historia = leer_version(spark, ruta_historia)
validar_historia(historia, modelo)
n_clientes = historia.count()
display(historia.where(F.col("id_cliente") == "<cliente_demo>").limit(10))
~~~

**Esperado:** una primera versión por cliente, ciudad Barcelona, actual y sin fecha de fin.
No se reconstruye la ciudad sobrescrita durante tipo1.
Repetir activación con el mismo ID/flag: `reutilizado`.

### Paso 3. A→B→A

El instructor actualiza ciudad y updated_at en SQL, esperando seis segundos después de cada cambio:

| Cambio | Lote | Secuencia |
|---|---|---|
| Barcelona → Valencia | <R>-crm-scd1 | Bronze → silver → nb_30_gold_dimension |
| Valencia → Barcelona | <R>-crm-scd2 | Bronze → silver → nb_30_gold_dimension |

A partir de la activación usar gold normal, no volver a activar.
Repetir gold scd1 antes del segundo cambio: debe conservar dos versiones.

Después de scd2:

~~~python
historia = leer_version(spark, ruta_historia)
validar_historia(historia, modelo)
cliente = historia.where(F.col("id_cliente") == "<cliente_demo>")
assert cliente.count() == 3
assert cliente.select("id_version").distinct().count() == 3
assert cliente.where(F.col("es_actual")).count() == 1
assert historia.count() == n_clientes + 2
display(cliente.orderBy("vigente_desde").limit(10))
~~~

**Esperado:** tres versiones y tres IDs, intervalos `[vigente_desde,vigente_hasta)`.
La configuración del ejemplo no carga email/nombre; la capacidad tipo1 se estudia en
`tests/unit/test_scd2.py::test_activacion_reintento_a_b_a_y_tipo1`.

~~~powershell
git add contracts/gold config/modelos docs/catalogo.md
git commit -m "Activa historia de ciudad y proyeccion actual"
~~~

**Pregunta:** ¿A→B→B→A produce tres o cuatro versiones? ¿Qué ocurre exactamente en la frontera de un intervalo?

## Demo 6 · Consumo · 200–220

El instructor muestra el modelo/informe preparado; no viene implementado en el repo.
Si no está disponible, realizar estas comprobaciones en Spark y distinguirlas de un informe publicado.

~~~python
actual = leer_version(spark, rutas.tabla(ctx_crm.entorno, "gold", "dim_cliente_actual"))
assert actual.count() == n_clientes
assert actual.groupBy("id_cliente").count().where("count > 1").count() == 0
display(actual.where(F.col("id_cliente") == "<cliente_demo>").limit(5))
~~~

La página actual muestra una fila con Barcelona; la histórica muestra tres versiones.
Las medidas técnicas cuentan `N` clientes y `N+2` versiones si no hubo otros cambios.
No crear relación muchos a muchos entre las dos dimensiones para simular una unión temporal.
El KPI/hecho de devoluciones no forma parte de la implementación.

**Pregunta:** ¿por qué contar filas de dim_cliente deja de contar clientes después de SCD2?

## Demo 7 · Revisión y pruebas · 220–235

~~~powershell
git log --oneline --max-count=6
git diff main...HEAD --stat
git diff main...HEAD -- contracts config
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py --comprobar
git add --all
& $Python -m pre_commit run --all-files
& $Python -m pytest --delta -q
~~~

Ejecutar la suite completa si Java/Hadoop están preparados. El instructor dispone del resultado del ensayo.
Si observas su log, anotar que es evidencia del instructor y su revisión, no de tu máquina.
Las 80 pruebas de referencia usan Delta local; SQL se simula en las pruebas de integración local.

Abrir `tests/unit/test_delta.py::test_migracion_y_recuperacion_tras_historia_antes_de_proyeccion`.
La excepción esperada ocurre después del histórico. El reintento completa la proyección sin duplicar historia.

**Pregunta:** ¿qué debe permanecer igual en un reintento gold? Lote, configuración, contrato y flag de operación.

## Cierre · 235–240

Guardar ficha y commits. El instructor restaura las filas SQL respaldadas y ejecuta cargas nuevas.
La cuarentena conserva evidencias; restaurar la ciudad original puede crear una cuarta versión SCD2.
Un nuevo Run no devuelve al estado inicial; no borrar tablas/control para intentar arreglar una demo.

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| No tengo recursos cloud | Continuar localmente y registrar las evidencias mostradas |
| No conecta a SQL | Comunicar identidad/base/runtime; no insertar contraseñas en el código |
| Q3 aparece en rojo | Es esperado; aplicar Q4 y reintentar el mismo lote |
| No puedo iniciar otro lote | Revisar el pendiente con el instructor |
| Cambié YAML y no cambia Fabric | Validar, publicar y recargar contexto |
| Gold no termina | Mantener lote y configuración; no activar un flag distinto |
| No salen 8/6 filas | Comparar N/R1/R2 reales; el lector no limita a diez IDs |
| El último incremental lee filas | Revisar solape y marca confirmada antes de esperar vacío |

## Evidencias que debes poder explicar

- [ ] Proyecto nuevo, IDs renovados, contratos activos.
- [ ] Defecto visible en SQL y bronze; cuarentena con motivo/versionado.
- [ ] Q2 retira filas antes válidas; Q3 no publica; Q4 recupera el pendiente.
- [ ] Marca confirmada tras silver, reintento y solape.
- [ ] Ciudad tipo1 convertida a SCD2; tres versiones A→B→A, un actual.
- [ ] Clientes actuales distintos de versiones históricas.
- [ ] Límites: timestamp no detecta borrados, sin historia retroactiva ni transacción distribuida.
