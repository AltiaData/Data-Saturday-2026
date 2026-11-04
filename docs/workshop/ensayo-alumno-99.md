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
| `alumno-99/demo-03` | Punto inicial de la demo 3: errores de origen y cuarentena Q1–Q4 | Pendiente |
| `alumno-99/demo-04` | Punto inicial de la demo 4: completa → incremental | Pendiente |
| `alumno-99/demo-05` | Punto inicial de la demo 5: activación SCD2 | Pendiente |
| `alumno-99/demo-06` | Punto inicial de la demo 6: consumo y documentos Cosmos | Pendiente |
| `alumno-99/demo-07` | Punto inicial de la demo 7: revisión del cambio | Pendiente |

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
| 19 | Demo 2 | `02_plan-sesion-4-horas.md` | Cada notebook tarda 90–115 s (arranque en frío) y más con reintentos: la demo 2 son 6 ejecuciones (unos 12–20 min de sus 25) | Revisar tiempos del plan al terminar el ensayo | Pendiente |

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
