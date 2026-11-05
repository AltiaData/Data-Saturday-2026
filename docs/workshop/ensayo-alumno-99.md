# Ensayo alumno-99 · Diario de cambios

Ensayo completo del workshop en el tenant propio del instructor, actuando como el alumno `alumno-99`.
Objetivos:

1. Disponer de un punto inicial reproducible para cada demo, de modo que una persona retrasada pueda incorporarse
   y continuar de forma autónoma.
2. Detectar incoherencias del contenido mediante un role-play al inicio de cada demo: seguir literalmente la
   documentación del alumnado y anotar cada fallo, cifra discrepante o paso implícito.

- Participante: Eladio Rincón Herrera (`erincon01`, eladio.rincon@gmail.com), en el papel de `alumno-99`.
- Cuentas del tenant propio (su ID solo en `.env.alumno`): `fabric-admin@midatalab.com` en el portal de Fabric;
  eladio.rincon@outlook.com (invitada, creadora del tenant) en la sesión de Azure CLI que creó los recursos.
- Proyecto: `fsh-alumno99`; workspaces `fsh-alumno99-datos-dev`, `fsh-alumno99-ing-dev`, `fsh-alumno99-ana-dev`.
- Rama base: `main` (`8313f6c`).

Los identificadores, IDs de workspace y datos del tenant se guardan solo en `.env.alumno` (ignorado por Git).

## Ramas

| Rama | Contenido | Estado |
|---|---|---|
| `alumno-99/setup` | Preparación previa (`01_antes-de-la-sesion.md`), correcciones y este diario (versión de referencia) | En curso |
| `alumno-99/demo-01` | Punto inicial de la demo 1: proyecto greenfield | Ensayada |
| `alumno-99/demo-02` | Punto inicial de la demo 2: carga completa CRM y tipo1 | Ensayada |
| `alumno-99/demo-03` | Punto inicial de la demo 3: errores de origen y cuarentena Q1–Q4 | Ensayada |
| `alumno-99/demo-04` | Punto inicial de la demo 4: completa → incremental | Ensayada |
| `alumno-99/demo-05` | Punto inicial de la demo 5: activación SCD2 | Ensayada |
| `alumno-99/demo-06` | Punto inicial de la demo 6: consumo y documentos Cosmos | Ensayada |
| `alumno-99/demo-07` | Punto inicial de la demo 7: revisión del cambio | Ensayada |

Desde `demo-02`, cada rama contiene el proyecto generado (`crear_proyecto.py`) tal como queda al empezar esa
demo. Las correcciones se hacen en `setup` y se fusionan en las ramas de demo.

## Estado en Fabric por demo

El punto inicial tiene dos partes: el estado del repositorio (contratos, configuración, CSV), que recoge cada rama,
y el estado en Fabric (tablas Delta, lotes, marcas, historia), que no se versiona en Git.

| Demo | Depende de | Lotes previos necesarios |
|---|---|---|
| 1 | Preparación | Ninguno |
| 2 | 1 | Ninguno |
| 3 | 1 | Ninguno (independiente de CRM) |
| 4 | 2 | `crm-base` |
| 5 | 4 | `crm-base`, `crm-inc-1`, `crm-inc-2` |
| 6 | 5 | Los anteriores más `crm-activar`, `crm-scd2-b`, `crm-scd2-a` |
| 7 | 1 | Ninguno (solo repositorio) |

## Hallazgos

| # | Demo | Fichero | Hallazgo | Acción | Estado |
|---|---|---|---|---|---|
| 1 | — | `templates/workshop/README.md` | Describe la edición SQL (`01_base` «SQL completo»), omite el paso `recuperar` y remite al runbook SQL | Actualizar a la edición CSV | Pendiente |
| 2 | — | `docs/workshop/03_validacion-edicion.md` | Falta el ensayo remoto en Fabric | Este ensayo | En curso |
| 3 | — | `docs/workshop/01_preparacion-instructores.md` | Redactado desde la copia privada del instructor y distribuido en el repo del alumnado | Decidir separación | Pendiente |
| 4 | Setup | `docs/workshop/01_antes-de-la-sesion.md` | Con cuenta corporativa y personal, Azure CLI seguía en el tenant corporativo | Aviso de `az account show` en la guía; el script lo comprueba | Hecho |
| 5 | Setup | `infra/` | El Terraform es de proyecto real (dev/test/prod, SP, grupos); no sirve al alumno. Los recursos se creaban a mano | `infra/lab/New-LabResources.ps1` y referencia en la guía | Hecho |
| 6 | Setup | Tenant | Coexisten una capacidad PPU y una Trial; la PPU no sirve para Fabric | El script descarta `PP*` y elige la única capacidad válida | Hecho |
| 7 | Setup | Identidades | Portal con `fabric-admin@midatalab.com`, CLI con la cuenta invitada de outlook: los workspaces solo tenían Admin para la cuenta de la CLI y no eran visibles en el portal | Aviso «misma cuenta en portal y CLI» y «sin cuentas personales» en la guía; el script rechaza cuentas `#EXT#`. El rol de administrador de Fabric no da acceso al contenido del workspace | Hecho: `fabric-admin` es Admin de los tres workspaces y la CLI usa esa cuenta |
| 8 | Setup | `docs/workshop/01_antes-de-la-sesion.md` | El paso 4 decía «selecciona un runtime soportado» sin indicar dónde ni cuál | Ubicación en Environment y workspace, Runtime 1.3 y orden respecto al wheel | Hecho |
| 9 | Setup | Fabric | Environment y workspace nacen en Runtime 2.0 (Spark 4, ANSI): no validado; riesgo en los casts de la cuarentena | El script fija 1.3 en `env_fwk` (publicado) y en el workspace; aviso en la guía. Validar 2.0 queda para otra edición | Hecho |
| 10 | Setup | `01_antes-de-la-sesion.md`, `01_preparacion-instructores.md` | Exigían `py -3.12`; el equipo de ensayo solo tenía 3.11 y 3.13 y los comandos siguientes seguían ejecutándose sin venv. `pyproject.toml` admite ≥ 3.10 y Runtime 1.3 usa 3.11 | Python 3.11 o 3.12, `py --list`, comprobación de que existe el venv | Hecho |
| 11 | Setup | Ídem | pip 22.3 del venv de 3.11: `MemoryError` al cachear `pyspark`; la instalación falla y `verificar` da `No module named 'datafwk'` | `pip install --upgrade pip` antes de instalar | Hecho |
| 12 | Setup | `01_antes-de-la-sesion.md` | `Copy-Item .env.alumno.example .env.alumno` sobrescribía el dotenv; el aviso venía después del comando | Copia condicionada a que no exista | Hecho |
| 13 | Setup | `01_antes-de-la-sesion.md` | La instalación tarda unos 7 minutos (descarga de `pyspark`); no se avisaba | Aviso de hacerla antes del evento | Hecho |
| 14 | Demo 1 | `scripts/laboratorio.py` | `laboratorio datos` falla con `FriendlyNameSupportDisabled`: mezclaba el GUID del workspace con el nombre `lh_bronze.Lakehouse`. `config` funcionaba porque usa nombres | `publicar_datos` usa el nombre del workspace, como `publicar_config` | Hecho |
| 15 | Demo 1 | `02_seguir-las-demos.md`, `02_plan-sesion-4-horas.md` | Publicar el wheel en `env_fwk` tarda unos 6 minutos (354 s) de los 35 del bloque; el resto de la publicación, menos de 1 minuto | Valorar publicar el wheel en la preparación previa | Pendiente |
| 16 | Demo 1 | `.env.alumno.example`, `.env.instructor.example`, `01_antes-de-la-sesion.md`, `02_seguir-las-demos.md` | `LAKEHOUSE_ESQUEMA=dbo` por defecto, pero los lakehouses que publica el repo no tienen esquemas (`lakehouse.metadata.json` vacío; API: `defaultSchema` vacío). Las tablas irían a `Tables/dbo/` y no aparecerían en el SQL endpoint | Valor por defecto vacío y explicación en las guías; proyecto generado reconfigurado y `config` publicado de nuevo | Hecho |
| 17 | Demo 2 | `02_seguir-las-demos.md`, `01_antes-de-la-sesion.md` | Trial FTL4: cada notebook lanzado justo después de otro falla con `TooManyRequestsForCapacity` (430); entra al reintentar 60 s después. En el portal la sesión interactiva sigue viva tras ejecutar, así que el siguiente notebook fallará siempre | Instrucción «una sesión cada vez: Stop session» y aviso del SKU en la preparación | Hecho |
| 18 | Demo 2 | `02_seguir-las-demos.md` | Los SQL endpoints no mostraban ninguna tabla minutos después de cargar; aparecieron al forzar la sincronización de metadatos | Instrucción concreta: botón Refresh del SQL analytics endpoint | Hecho |
| 19 | Demo 2 | `02_plan-sesion-4-horas.md` | Cada notebook tarda 90–115 s (arranque en frío) y más con reintentos: la demo 2 son 6 ejecuciones (unos 12–20 min de sus 25) | Revisar tiempos del plan al terminar el ensayo | Tiempos documentados; recorte pendiente de decisión |
| 20 | Demo 3 | `02_seguir-las-demos.md` | La cuarentena guarda el lote de observación (`dev-q1`), no el de revalidación: filtrar por `dev-q2` devuelve cero | Consulta por `batch_id` y `version_contrato` con el resultado esperado | Hecho |
| 21 | Demo 3 | `02_seguir-las-demos.md` | Q3 hablaba de «lote pendiente», pero el estado real es `revalidacion`; la API de jobs solo da un error genérico y el mensaje de contrato está en la salida del notebook | Estado, mensaje y tablas de auditoría explícitos | Hecho |
| 22 | Demo 3 | `02_seguir-las-demos.md` | Los pasos Q3 y Q4 no validaban contratos ni regeneraban el catálogo: el hook `catalogo-actualizado` falla | `validar_contratos` y `generar_catalogo` en ambos pasos | Hecho |
| 23 | Demo 1–3 | `scripts/laboratorio.py`, `templates/workshop/` | Todo YAML generado incumplía `yamllint`: plantillas con listas sin sangrar y `yaml.safe_dump` sin sangría (y CRLF en `recuperar`). `pre-commit --all-files` de la demo 7 fallaría | `escribir_yaml` (listas sangradas, LF, ancho 120) en todas las escrituras; plantillas reformateadas; test que aplica todos los checkpoints y pasa `yamllint` | Hecho |
| 24 | Demo 3 | `templates/workshop/*/contracts` | Descripciones «observada en SQL» en la edición CSV, sin tildes, y Q3 con el texto de Q2 | Texto corregido (solo `descripcion`; sin cambio de contrato para consumidores) | Hecho |
| 25 | Demo 4 | `02_seguir-las-demos.md` | La guía no decía cómo comprobar ventana, solape ni repetición | Consultas de `fwk_lotes` y `fwk_ejecuciones` con lo esperado (`reutilizado`) | Hecho |
| 26 | Demo 4 | `data/README.md` | Dice que un reintento «reutiliza bronze y no vuelve a leer el CSV», pero la auditoría de la repetición de `crm-inc-1` registra bronze `ok` con 1 fila leída (sin duplicar); solo silver y gold aparecen `reutilizado` | Revisar la frase con el comportamiento real del framework | Pendiente |
| 27 | Demo 4 | `02_plan-sesion-4-horas.md` | Demo 4: 9 ejecuciones, 3 con reintento por 430; unos 25 min de cómputo de los 30 del bloque (amplía el hallazgo 19) | Consolidar con el plan | Tiempos documentados; recorte pendiente de decisión |
| 28 | Demo 5 | `02_seguir-las-demos.md` | Mejora de contenido: la guía no pedía revisar el diff del checkpoint SCD2, que es la pieza que explica el cambio de grano (clave `id_cliente` → `id_version`) y su impacto en consumidores | `git diff` de contratos gold y modelo, con tres puntos de lectura | Hecho |
| 29 | Demo 5 | `templates/workshop/05_scd2/contracts/gold/dim_cliente.yml` | Descripciones de columnas sin tildes («version», «observacion», «unica») | Corregidas (solo `descripcion`) | Hecho |
| 30 | Demo 5 | `02_plan-sesion-4-horas.md` | Demo 5: 13 ejecuciones (5 reintentos por 430), unos 35 min de cómputo para un bloque de 40 | Consolidar con el plan: es el bloque que más excede | Tiempos documentados; recorte pendiente de decisión |
| 31 | Demo 6 | `data/README.md` | El ejemplo de lectura Cosmos reasignaba `documentos` en cada parte: solo quedaban los de la última | Acumula con `extend` e imprime el total (9.050 en `eventos_web`) | Hecho |
| 32 | Demo 6 | `02_seguir-las-demos.md` | Mejora de contenido: la multiplicación de filas al unir con el histórico solo se explicaba; las devoluciones no tienen `id_cliente` para mostrarla con un hecho | Consulta `dim_cliente_actual` ⨝ `dim_cliente` por `id_cliente` (102 frente a 100) y su corrección con `es_actual` | Hecho |
| 33 | Demo 7 | `scripts/generar_catalogo.py` | En Windows escribía CRLF: `git status` marcaba `docs/catalogo.md` modificado sin cambios de contenido, justo cuando la demo pide revisar `git status` | Escritura con LF | Hecho |
| 34 | Demo 7 | `tests/conftest.py` | Sin Java, `pytest` daba 14 errores (`JAVA_GATEWAY_EXITED`), también en `main` | Los tests de Spark se omiten con motivo si no hay Java; CI no cambia | Hecho |
| 35 | Demo 7 | `02_seguir-las-demos.md` | Sin Terraform/tflint, sus hooks fallan con código 127 y la guía no decía cómo proceder | Explicación y `SKIP` solo de esos tres hooks, con validación completa en CI | Hecho |
| 36 | — | `03_validacion-edicion.md` | El pendiente «pre-commit completamente verde» ya se cumple salvo Terraform (sin `WinError 4551`) | Actualizar el documento de validación al consolidar | Pendiente |

## Registro

### 2026-11-04 · Preparación

- Creada la rama `alumno-99/setup` desde `main` (`8313f6c`).
- Creado `.env.alumno` con el tenant propio y `PROYECTO=fsh-alumno99`. Pendientes: capacidad, IDs de los tres
  workspaces y del Environment `env_fwk`.
- Riesgo a vigilar: la sesión de Azure CLI debe usar la cuenta del tenant propio, no la corporativa
  (`az account show` antes de publicar). Se materializó: la CLI estaba en el tenant corporativo (hallazgo 4).
- Añadido `infra/lab/New-LabResources.ps1`. Ejecutado con `-WhatIf` y después en real: creados
  `fsh-alumno99-datos-dev`, `fsh-alumno99-ing-dev`, `fsh-alumno99-ana-dev` en la capacidad Trial (FTL4) y `env_fwk`
  en ingeniería; IDs escritos en `.env.alumno`. Segunda ejecución: todo «existente», sin cambios (idempotente).
- Pendiente en portal: runtime de `env_fwk` y comprobar rol Admin en los tres workspaces.
- Detectado que el portal se usa con `fabric-admin@midatalab.com` (Fabric no admite la cuenta personal de outlook)
  y que esa cuenta no tenía rol en los workspaces (hallazgo 7). Documentado dónde se configura el runtime de Spark
  (hallazgo 8). Concesión de Admin por API: bloqueada por el modo automático y repetida con autorización expresa del instructor;
  `fabric-admin` es ahora Admin de los tres workspaces. El script rechaza ya la cuenta invitada de la CLI.
- CLI pasada a `fabric-admin@midatalab.com`; el script lo encuentra todo «existente». `env_fwk` y el workspace
  estaban en Runtime 2.0: fijado 1.3 y publicado `env_fwk` (estado `Success`). El script lo hace ya por sí mismo.
- Role-play de la preparación local (sección 1): `py -3.12` falla (hallazgo 10); con 3.11, `pip install` falla por
  `MemoryError` (11); tras actualizar pip, instalación correcta en unos 7 minutos y `modificar_csv verificar`:
  «Volcado íntegro: hashes, recuentos y documentos JSON correctos».
- `pre-commit run --files` sobre los ficheros cambiados: todo en verde. `gitleaks` y `check-merge-conflict` se
  ejecutaron sin el bloqueo `WinError 4551` que recoge `03_validacion-edicion.md`; falta repetir `--all-files`.

### 2026-11-04 · Demo 1 (rama `alumno-99/demo-01`)

- Parte local (`crear_proyecto`, `pip install`, `configurar`, `checkpoint base`, `preparar`, `validar_contratos`,
  `generar_catalogo`) en `C:\src\TRIBUS\fsh-alumno99-lab`: sin errores, 33 s.
- Publicación: `lakehouses` 24 s, `build` 5 s, `wheel` 354 s (hallazgo 15), `notebooks` 11 s, `config` 15 s.
  `datos` falló (hallazgo 14); corregido en `setup` y repetido con éxito.
- Lakehouses sin esquemas y `LAKEHOUSE_ESQUEMA=dbo` (hallazgo 16): corregido en `setup`; `configurar` y `config`
  repetidos en el proyecto generado.
- Vinculación de los cinco notebooks a `env_fwk` hecha en el portal por el instructor; verificada por API
  (`getDefinition`: los cinco referencian `env_fwk`; sin lakehouse por defecto, no necesario).
- Creada `alumno-99/demo-02` con el proyecto generado (28 ficheros respecto a `demo-01`); antes, comprobado que
  ningún fichero versionable contiene IDs del tenant y sincronizados desde `setup` los cuatro ficheros desfasados.

### 2026-11-05 · Demo 2 (rama `alumno-99/demo-02`)

- Notebooks ejecutados con la API de jobs de Fabric (`RunNotebook` con parámetros), prototipo de `alcanzar`.
- `crm-base`: bronze 112 s, silver 115 s, gold falló con 430 (hallazgo 17) y completó al reintentar (107 s).
- Tablas en OneLake bajo `Tables/` sin subcarpeta `dbo` (confirma el hallazgo 16). SQL endpoints vacíos hasta forzar
  la sincronización de metadatos (hallazgo 18).
- Resultados: bronze 100 observaciones; silver 100 clientes; `dim_cliente` 100 filas y `C0001` en Sevilla;
  `fwk_lotes` con `crm-base` confirmado (completa, contrato v1); marca registrada. Coincide con la guía.
- Repetición de `crm-base` (bronze 88 s; silver y gold con un reintento por 430): 100 filas y 100 claves en las tres
  capas, un único lote, misma marca; `fwk_ejecuciones` registra 6 ejecuciones. Idempotencia confirmada.

### 2026-11-05 · Demo 3 (rama `alumno-99/demo-03`)

- Desde aquí el ensayo se ejecuta sobre la rama (copia de trabajo del repositorio), no sobre `fsh-alumno99-lab`.
- `defectos` + `datos`; `dev-q1`: bronze 105 s, silver 121 s. 397 leídas, 387 válidas, 10 a cuarentena (v1).
- Q2 (`dev-q2`, 123 s): 358 válidas; 39 rechazos v2 con lote `dev-q1` (hallazgo 20). Marca sin cambios.
  Repetición (87 s): sin evidencia duplicada.
- Q3 (`dev-q3`, 108 s): falla; silver 358; lote `dev-q3` en `revalidacion`; ejecución `error` con «39 filas
  incumplen el contrato; no se publica» (hallazgo 21).
- Q4 (`dev-q3` repetido, 115 s): confirmado con contrato v4; 358 válidas y 39 rechazos v4. Coincide con la guía.
- Al guardar `demo-04`, `yamllint` falló sobre el contrato generado (hallazgo 23); corregido en `setup`.

### 2026-11-05 · Demo 4 (rama `alumno-99/demo-04`)

- `checkpoint incremental`: diff de una línea en `config/fuentes/crm.yml` (el formato YAML se conserva).
- `crm-inc-1` (110 s, 227 s con un 430, 110 s): ventana desde la marca menos 5 s; bronze y silver 1 fila; 100 clientes;
  `C0001` en Barcelona; marca avanzada.
- Repetición de `crm-inc-1` (unos 92 s cada notebook): bronze sigue con 1 fila del lote; silver y gold `reutilizado`;
  marca sin cambios (hallazgo 26 sobre la redacción de `data/README.md`).
- `crm-inc-2` sin cambios (tras 12 s; dos reintentos por 430): 0 filas en bronze y silver; silver 100; marca avanzada.
- Creada `alumno-99/demo-05` con CRM en incremental.

### 2026-11-05 · Demo 5 (rama `alumno-99/demo-05`)

- `checkpoint scd2`: cambian modelo y contrato `dim_cliente`; nuevo contrato `dim_cliente_actual`; 19 YAML publicados.
- `crm-activar`: bronze 108 s, silver 108 s, activación 264 s (un 430) y repetida 108 s. 100 versiones, 100 actuales,
  `C0001` en Barcelona; la repetición no crea versiones; `fwk_modelos` registra la migración.
- Valencia + `crm-scd2-b` (108, 123, 168 s) y repetición (dos 430): Barcelona cerrada y Valencia vigente, sin duplicar.
- Barcelona + `crm-scd2-a` (un 430): `C0001` con tres versiones contiguas e identificadores distintos; 102 históricas,
  100 en `dim_cliente_actual`; ningún cliente con más de una vigente. Coincide con la guía.
- Creada `alumno-99/demo-06`.

### 2026-11-05 · Demo 6 (rama `alumno-99/demo-06`)

- Sin notebooks. `dim_cliente_actual` 100; `dim_cliente` 102; `C0001` 3 filas. Manifiesto con 10 contenedores Cosmos
  y su `partition_key_paths`. `modificar_csv verificar`: volcado íntegro.
- Ejemplo de `data/README.md` defectuoso (hallazgo 31); consulta de multiplicación añadida (hallazgo 32).
- Contrato SCD2 del proyecto actualizado con las descripciones corregidas. Creada `alumno-99/demo-07`.

### 2026-11-05 · Demo 7 (rama `alumno-99/demo-07`)

- `generar_catalogo`, `validar_contratos` y `agente_lint` correctos; `.env.alumno` y `data/laboratorio` ignorados.
- `docs/catalogo.md` aparecía modificado solo por CRLF (hallazgo 33).
- `pytest`: 14 errores por falta de Java (hallazgo 34); tras la corrección, 73 correctos y 17 omitidos.
- `pre-commit run --all-files`: todo en verde salvo los hooks de Terraform, no instalado (hallazgo 35).

## Resumen del ensayo

Las siete demos reproducen en Fabric los resultados que promete la guía (100 clientes; Q1 387/10, Q2 358/39, Q3 fallo
con lote en `revalidacion`, Q4 recuperado; incremental de una fila y ventana vacía; SCD2 con 102 versiones y 100
vigentes). Quedan pendientes de consolidar los hallazgos 1, 3, 15, 19, 26, 27, 30 y 36: material del instructor,
README de `templates/workshop` y, sobre todo, los tiempos del plan con capacidades pequeñas.

### 2026-11-05 · Tiempos

- Tiempos medidos añadidos a cada demo de `02_seguir-las-demos.md` y tabla comparativa en `02_plan-sesion-4-horas.md`,
  con el entorno del ensayo (Trial FTL4, West Europe, Runtime 1.3). La restauración no se ha ensayado.
