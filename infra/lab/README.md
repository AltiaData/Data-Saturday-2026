# Recursos Fabric del laboratorio

`New-LabResources.ps1` prepara, en el tenant propio de cada alumno, los recursos que exige
[la preparación](../../docs/workshop/01_antes-de-la-sesion.md): tres workspaces en dev asignados a una capacidad Fabric
activa y el Environment `env_fwk` en el de ingeniería. Escribe sus IDs en el dotenv del alumno.

El Terraform de `infra/` es la referencia para un proyecto real (dev, test y prod, service principal y grupos de Entra)
y no se usa en el laboratorio: un alumno no dispone de esa identidad ni necesita Terraform instalado.

## Requisitos

- PowerShell 7.2 o superior y Azure CLI, los mismos de la preparación.
- `.env.alumno` con `AZURE_TENANT_ID`, `PROYECTO` y `ENTORNO=dev`.
- Una capacidad Fabric activa (F, FT de prueba o P). Premium Per User (`PP*`) no sirve y se descarta.
- Permiso en el tenant para crear workspaces.

## Uso

Desde la raíz del repositorio:

```powershell
az login --tenant '<tu-tenant-id>' --allow-no-subscriptions
pwsh ./infra/lab/New-LabResources.ps1 -WhatIf   # muestra qué crearía, sin cambios
pwsh ./infra/lab/New-LabResources.ps1
```

Si hay varias capacidades activas y `FABRIC_CAPACITY_ID` no está cumplimentado, añade `-CapacityName '<nombre>'`.

## Comportamiento

- Comprueba que la sesión de Azure CLI está en el tenant del dotenv y que no es una cuenta invitada (`#EXT#`), como
  una cuenta personal de Microsoft, que Fabric no admite; si no, se detiene sin crear nada.
- Nombres: `WORKSPACE_*_NOMBRE` si están informados; si no, `<PROYECTO>-datos-dev`, `-ing-dev` y `-ana-dev`.
- Idempotente: reutiliza los recursos existentes con el mismo nombre y reasigna la capacidad si difiere.
- Escribe `FABRIC_CAPACITY_ID`, `WS_DATOS_ID`, `WS_ING_ID`, `WS_ANA_ID` y `ENV_FWK_ID`; conserva el resto del fichero.
- No borra recursos, no publica items ni datos y no guarda tokens. El script no contiene datos de ningún tenant.

La cuenta de la sesión de Azure CLI queda como única Admin de los workspaces. Inicia sesión en la CLI con la misma
cuenta que usarás en el portal; si no, añade la del portal como Admin en *Manage access* de cada workspace.

Fija el runtime de Spark (`-RuntimeVersion`, por defecto `1.3`: Spark 3.5) en `env_fwk`, que publica y espera, y como
valor por defecto del workspace de ingeniería. El valor por defecto de Fabric es 2.0 (Spark 4), no validado con el
framework. Detalle en el paso 4 de la preparación.
