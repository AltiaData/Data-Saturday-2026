# Preparación del alumno · Fabric propio obligatorio

La única modalidad es ejecutar en tu propia suscripción/capacidad de Microsoft Fabric. Trae una cuenta de tu tenant,
capacidad activa asignable a tus workspaces y permisos para crear y ejecutar lakehouses, notebooks y Environments.
Una licencia Power BI Pro o PPU por sí sola no proporciona la capacidad de Fabric necesaria. Una capacidad Trial propia
sirve si tu tenant permite activarla y sigue vigente durante el evento. Consulta las
[licencias y capacidades de Fabric](https://learn.microsoft.com/en-us/fabric/enterprise/licenses).
Los alumnos no necesitan bases de Azure SQL, cuentas Cosmos ni credenciales de los instructores.

## 1. Herramientas antes del evento

Instala Git, PowerShell 7, Python 3.12, Azure CLI y un editor. Para pruebas locales Spark: Java 17 y dependencias dev;
en Windows, las utilidades nativas de Hadoop, o usa el devcontainer Linux incluido. Esto debe resolverse antes del evento.
La ejecución de las demos ocurre en Fabric; no depende de tener Spark local.

Desde la raíz de tu copia de alumnos o de la plantilla:

```powershell
$Plantilla = (Get-Location).Path
py -3.12 -m venv .venv
$Python = Join-Path $Plantilla '.venv\Scripts\python.exe'
$env:PATH = "$Plantilla\.venv\Scripts;$env:PATH"
& $Python -m pip install -e '.[dev,deploy]' build
& $Python -m scripts.modificar_csv verificar
Copy-Item .env.alumno.example .env.alumno
```

No sobrescribas `.env.alumno` si ya lo cumplimentaste. Es dotenv, no un script: no lo ejecutes con dot-sourcing.
Los valores entre `<...>` son marcadores pendientes. Nunca escribas tokens o contraseñas en YAML ni notebooks.

## 2. Tu fichero de entorno

Completa `.env.alumno` con estos datos:

| Campo | Dónde obtenerlo / uso |
|---|---|
| `AZURE_TENANT_ID` | Identificador de tu directorio Entra; la sesión CLI debe usar este tenant |
| `FABRIC_CAPACITY_ID` | Capacidad propia activa; referencia para asignarla manualmente en Fabric |
| `PROYECTO` | Nombre único, por ejemplo `fsh-alumno01`; letras minúsculas, números y guiones |
| `ENTORNO` | `dev` para estas demos |
| `WORKSPACE_*_NOMBRE` | Déjalos vacíos para derivar `<PROYECTO>-datos/ing/ana-dev`, o indica los nombres exactos |
| `WS_DATOS_ID`, `WS_ING_ID`, `WS_ANA_ID` | GUID de cada workspace creado; se ve en su URL/configuración |
| `ENV_FWK_ID` | GUID del Environment `env_fwk` creado en ingeniería |
| `LAKEHOUSE_ESQUEMA` | `dbo` si los lakehouses tienen esquemas; vacío si no los tienen |
| `DATA_ROOT` | `data`, relativo a la raíz del proyecto desde la que ejecutarás los comandos |

`FABRIC_CAPACITY_ID` es una referencia de preparación: los scripts no compran ni asignan capacidades.
El alumno realiza esa asignación en el portal y comprueba que la capacidad está activa.

## 3. Recursos propios antes de empezar

1. En Fabric crea tres workspaces vacíos con los nombres elegidos: datos, ingeniería y analítica.
2. Asígnalos a tu capacidad activa y comprueba que tu cuenta es administradora de los tres.
3. En ingeniería crea un Environment llamado `env_fwk`. Anota su ID en `.env.alumno`.
4. Selecciona el runtime de Spark y valida las pruebas de humo antes del evento. Las pruebas locales del repositorio
   usan Spark 3.5/Delta 3.3.2; no certifican automáticamente cualquier runtime cloud. El runtime se fija en dos sitios:
   - **Environment** (el que usan los notebooks): abre `env_fwk` en el workspace de ingeniería, elige en el
     desplegable **Runtime** de la pestaña *Home* la versión con Spark 3.5 (Runtime 1.3: Spark 3.5, Delta 3.2,
     Python 3.11), guarda y pulsa **Publish**. La publicación tarda unos minutos.
   - **Workspace** (valor por defecto): *Workspace settings → Data Engineering/Science → Spark settings →
     Environment*. Pon el mismo runtime. Opcionalmente, activa *Set default environment* con `env_fwk` para que los
     notebooks lo usen sin vincularlos uno a uno.

   El valor por defecto actual es Runtime 2.0 (Spark 4, modo ANSI activo), con el que el framework no está
   validado: cámbialo. `infra/lab/New-LabResources.ps1` lo hace en ambos sitios y publica el Environment.
   Elige el runtime **antes** de publicar el wheel: cambiarlo después obliga a publicar de nuevo el Environment.
   La librería exige Python 3.10 o superior, compatible con Runtime 1.3. Comprueba en el portal los nombres
   vigentes de los runtimes: Microsoft los renueva periódicamente.
5. Conserva los workspaces sin datos del workshop: el greenfield publicará los items durante la primera demo.
6. Autentícate con tu tenant; si no tienes una suscripción Azure de facturación, permite una sesión sin suscripciones:

```powershell
az login --tenant '<tu-tenant-id>' --allow-no-subscriptions
```

El inicio de sesión puede pedir MFA. Usa el mismo tenant en portal y CLI. Véase
[inicio de sesión con Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively).
No pegues tokens en el fichero de entorno. Comprueba la cuenta activa con `az account show`: si usas también una
cuenta corporativa, la CLI puede seguir en otro tenant. Usa **la misma cuenta** en el portal y en la CLI: los
workspaces creados desde la CLI solo dan rol Admin a esa cuenta. El rol de administrador de Fabric permite verlos
en el portal de administración, pero no abrir ni ejecutar su contenido. Fabric no admite cuentas personales de
Microsoft (outlook.com, hotmail.com): si creaste el tenant con una, crea en él una cuenta de la organización y úsala
en ambos sitios.

Los pasos 1 a 3 pueden automatizarse una vez iniciada la sesión: `pwsh ./infra/lab/New-LabResources.ps1` crea los tres
workspaces y `env_fwk` si no existen y escribe sus IDs en `.env.alumno`. Ejecútalo antes con `-WhatIf` para ver qué hará.
El runtime del Environment se sigue eligiendo en el portal. Detalle en [infra/lab](../../infra/lab/README.md).

## 4. Qué debes tener al llegar

- `.env.alumno` cumplimentado y fuera de Git; tres workspaces propios y capacidad activa.
- Environment `env_fwk` creado; Python, paquetes y autenticación probados.
- `python -m scripts.modificar_csv verificar` termina correctamente.
- La carpeta `data/original` contiene el volcado distribuido; aún no hay modificaciones ni cargas de las demos.

La siguiente guía es [Seguir las demos](02_seguir-las-demos.md). El instructor no entrega credenciales ni workspaces
compartidos como alternativa a esta preparación.
