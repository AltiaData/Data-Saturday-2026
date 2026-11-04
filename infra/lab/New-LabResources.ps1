#Requires -Version 7.2
<#
.SYNOPSIS
    Crea los recursos Fabric del laboratorio de un alumno y escribe sus IDs en el dotenv.

.DESCRIPTION
    Lee el dotenv del alumno (por defecto .env.alumno), comprueba que la sesión de Azure CLI está en su tenant y,
    si no existen, crea:
      - los tres workspaces <PROYECTO>-datos-dev, <PROYECTO>-ing-dev y <PROYECTO>-ana-dev (o los nombres indicados
        en WORKSPACE_*_NOMBRE), asignados a la capacidad;
      - el Environment env_fwk en el workspace de ingeniería;
      - el runtime de Spark (por defecto 1.3, Spark 3.5) en env_fwk, que publica, y en el workspace de ingeniería.
    Después escribe FABRIC_CAPACITY_ID, WS_DATOS_ID, WS_ING_ID, WS_ANA_ID y ENV_FWK_ID en el dotenv.

    Es idempotente: reutiliza los recursos que ya existen con el mismo nombre y reasigna la capacidad si difiere.
    No borra nada, no publica items ni datos y no escribe tokens. Los datos del tenant viven solo en el dotenv.

.PARAMETER EnvFile
    Ruta del dotenv del alumno. Se lee como texto: nunca se ejecuta.

.PARAMETER CapacityName
    Nombre de la capacidad cuando hay varias activas y FABRIC_CAPACITY_ID no está cumplimentado.

.EXAMPLE
    az login --tenant '<tu-tenant-id>' --allow-no-subscriptions
    pwsh ./infra/lab/New-LabResources.ps1 -WhatIf
    pwsh ./infra/lab/New-LabResources.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$EnvFile = '.env.alumno',
    [string]$CapacityName,
    [string]$EnvironmentName = 'env_fwk',
    [string]$RuntimeVersion = '1.3'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$FabricApi = 'https://api.fabric.microsoft.com/v1'
$FabricResource = 'https://api.fabric.microsoft.com'
$Description = 'Laboratorio del workshop del framework datafwk. Creado por infra/lab/New-LabResources.ps1.'
$WorkspaceRoles = [ordered]@{ DATOS = 'datos'; ING = 'ing'; ANA = 'ana' }

function Read-DotEnv([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "No existe $Path; copia primero .env.alumno.example"
    }
    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path -Encoding utf8) {
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$') {
            $values[$Matches[1]] = $Matches[2].Trim()
        }
    }
    $values
}

function Test-Pending([string]$Value) {
    [string]::IsNullOrWhiteSpace($Value) -or $Value.Contains('<')
}

function Get-Required([hashtable]$Values, [string]$Key) {
    $value = if ($Values.ContainsKey($Key)) { $Values[$Key] } else { '' }
    if (Test-Pending $value) { throw "Completa $Key en $EnvFile" }
    $value
}

function Set-DotEnvValues([string]$Path, [hashtable]$Updates) {
    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.AddRange([string[]](Get-Content -LiteralPath $Path -Encoding utf8))
    foreach ($key in $Updates.Keys) {
        $line = "$key=$($Updates[$key])"
        $index = -1
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "^\s*$([regex]::Escape($key))\s*=") { $index = $i; break }
        }
        if ($index -ge 0) { $lines[$index] = $line } else { $lines.Add($line) }
    }
    $fullPath = (Resolve-Path -LiteralPath $Path).Path
    [System.IO.File]::WriteAllLines($fullPath, $lines, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-Fabric([string]$Method, [string]$Path, [object]$Body = $null) {
    $request = @{
        Method                  = $Method
        Uri                     = "$FabricApi/$Path"
        Headers                 = @{ Authorization = "Bearer $script:Token" }
        ContentType             = 'application/json'
        StatusCodeVariable      = 'statusCode'
        ResponseHeadersVariable = 'responseHeaders'
    }
    if ($null -ne $Body) { $request.Body = $Body | ConvertTo-Json -Depth 5 }
    $response = Invoke-RestMethod @request
    if ($statusCode -eq 202 -and $responseHeaders.ContainsKey('Location')) {
        Wait-FabricOperation ([string]$responseHeaders['Location'][0])
        return $null
    }
    $response
}

function Wait-FabricOperation([string]$Location) {
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        Start-Sleep -Seconds 5
        $operation = Invoke-RestMethod -Method Get -Uri $Location -Headers @{ Authorization = "Bearer $script:Token" }
        if ($operation.status -eq 'Succeeded') { return }
        if ($operation.status -in 'Failed', 'Cancelled') {
            throw "Operación de Fabric $($operation.status): $($operation | ConvertTo-Json -Depth 5 -Compress)"
        }
    }
    throw 'La operación de Fabric no terminó en cinco minutos; vuelve a ejecutar el script.'
}

function Get-FabricCollection([string]$Path) {
    $items = [System.Collections.Generic.List[object]]::new()
    $uri = $Path
    while ($uri) {
        $page = Invoke-Fabric 'Get' $uri
        foreach ($item in $page.value) { $items.Add($item) }
        $token = $page.PSObject.Properties['continuationToken']
        $uri = if ($token -and $token.Value) { "${Path}?continuationToken=$([uri]::EscapeDataString($token.Value))" } else { $null }
    }
    $items.ToArray()
}

function Set-SparkRuntime([string]$WorkspaceId, [string]$EnvironmentId) {
    # Runtime 2.0 (Spark 4, ANSI activo) es el valor por defecto actual y el framework no está validado con él.
    $settingsPath = "workspaces/$WorkspaceId/spark/settings"
    if ((Invoke-Fabric 'Get' $settingsPath).environment.runtimeVersion -ne $RuntimeVersion) {
        if ($PSCmdlet.ShouldProcess('workspace de ingeniería', "Runtime por defecto $RuntimeVersion")) {
            Invoke-Fabric 'Patch' $settingsPath @{ environment = @{ runtimeVersion = $RuntimeVersion } } | Out-Null
            Write-Host "Runtime por defecto del workspace: $RuntimeVersion"
        }
    }
    $environmentPath = "workspaces/$WorkspaceId/environments/$EnvironmentId"
    if ((Invoke-Fabric 'Get' "$environmentPath/sparkcompute").runtimeVersion -eq $RuntimeVersion) {
        Write-Host "Runtime de ${EnvironmentName}: $RuntimeVersion"
        return
    }
    if (-not $PSCmdlet.ShouldProcess($EnvironmentName, "Publicar con runtime $RuntimeVersion")) { return }
    Invoke-Fabric 'Patch' "$environmentPath/staging/sparkcompute" @{ runtimeVersion = $RuntimeVersion } | Out-Null
    Invoke-Fabric 'Post' "$environmentPath/staging/publish" | Out-Null
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Seconds 15
        $state = (Invoke-Fabric 'Get' $environmentPath).properties.publishDetails.state
        if ($state -notin 'Running', 'Waiting') { break }
    }
    if ($state -ne 'Success') { throw "La publicación de $EnvironmentName terminó en estado $state" }
    Write-Host "Runtime de ${EnvironmentName} publicado: $RuntimeVersion"
}

function Resolve-Capacity([hashtable]$Values) {
    $capacities = Get-FabricCollection 'capacities'
    $configured = if ($Values.ContainsKey('FABRIC_CAPACITY_ID')) { $Values['FABRIC_CAPACITY_ID'] } else { '' }
    if (-not (Test-Pending $configured)) {
        $capacity = $capacities | Where-Object id -EQ $configured
        if (-not $capacity) { throw "FABRIC_CAPACITY_ID no corresponde a ninguna capacidad visible para tu cuenta" }
    }
    else {
        # PPU (PP*) no admite items de Fabric: lakehouses, notebooks ni Environments.
        $eligible = @($capacities | Where-Object { $_.state -eq 'Active' -and $_.sku -notlike 'PP*' })
        if ($CapacityName) { $eligible = @($eligible | Where-Object displayName -EQ $CapacityName) }
        if ($eligible.Count -ne 1) {
            $capacities | Format-Table displayName, sku, state | Out-Host
            throw 'No hay una única capacidad Fabric activa: indica -CapacityName o FABRIC_CAPACITY_ID en el dotenv'
        }
        $capacity = $eligible[0]
    }
    if ($capacity.state -ne 'Active') { throw "La capacidad $($capacity.displayName) no está activa ($($capacity.state))" }
    if ($capacity.sku -like 'PP*') { throw "La capacidad $($capacity.displayName) es Premium Per User: no sirve para Fabric" }
    $capacity
}

$values = Read-DotEnv $EnvFile
$tenantId = Get-Required $values 'AZURE_TENANT_ID'
$project = Get-Required $values 'PROYECTO'
if ($project -cnotmatch '^[a-z][a-z0-9-]{2,39}$') {
    throw 'PROYECTO: entre 3 y 40 letras minúsculas, números o guiones'
}
if ((Get-Required $values 'ENTORNO') -ne 'dev') { throw 'El laboratorio docente se crea únicamente en dev' }

$account = az account show --query '{tenant:tenantId, user:user.name}' -o json 2>$null | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or -not $account) {
    throw "No hay sesión de Azure CLI: az login --tenant '<AZURE_TENANT_ID>' --allow-no-subscriptions"
}
if ($account.tenant -ne $tenantId) {
    throw "La sesión de Azure CLI ($($account.user)) está en otro tenant. Ejecuta az login con el tenant de $EnvFile"
}
$principalName = az ad signed-in-user show --query userPrincipalName -o tsv 2>$null
if ($principalName -and $principalName.Contains('#EXT#')) {
    # Fabric no admite cuentas personales de Microsoft: el portal no las deja entrar y serían las únicas Admin.
    throw "La CLI usa una cuenta invitada ($($account.user)). Inicia sesión con una cuenta de la organización del tenant."
}
$script:Token = az account get-access-token --resource $FabricResource --query accessToken -o tsv
if ($LASTEXITCODE -ne 0 -or -not $script:Token) { throw 'No se pudo obtener un token de Fabric con Azure CLI' }
Write-Host "Sesión: $($account.user)"

$capacity = Resolve-Capacity $values
Write-Host "Capacidad: $($capacity.displayName) ($($capacity.sku), $($capacity.state))"

$updates = @{ FABRIC_CAPACITY_ID = $capacity.id }
$existingWorkspaces = Get-FabricCollection 'workspaces'
$workspaceIds = @{}
foreach ($role in $WorkspaceRoles.Keys) {
    $nameKey = "WORKSPACE_${role}_NOMBRE"
    $name = if ($values.ContainsKey($nameKey) -and $values[$nameKey]) { $values[$nameKey] } else { "$project-$($WorkspaceRoles[$role])-dev" }
    $workspace = $existingWorkspaces | Where-Object displayName -EQ $name | Select-Object -First 1
    if (-not $workspace) {
        if ($PSCmdlet.ShouldProcess($name, "Crear workspace en $($capacity.displayName)")) {
            $workspace = Invoke-Fabric 'Post' 'workspaces' @{
                displayName = $name; description = $Description; capacityId = $capacity.id
            }
            Write-Host "Workspace creado: $name"
        }
    }
    else {
        $currentCapacity = $workspace.PSObject.Properties['capacityId']
        if (-not $currentCapacity -or $currentCapacity.Value -ne $capacity.id) {
            if ($PSCmdlet.ShouldProcess($name, "Asignar a la capacidad $($capacity.displayName)")) {
                Invoke-Fabric 'Post' "workspaces/$($workspace.id)/assignToCapacity" @{ capacityId = $capacity.id } | Out-Null
                Write-Host "Workspace reasignado: $name"
            }
        }
        else {
            Write-Host "Workspace existente: $name"
        }
    }
    if ($workspace) {
        $workspaceIds[$role] = $workspace.id
        $updates["WS_${role}_ID"] = $workspace.id
    }
}

if ($workspaceIds.ContainsKey('ING')) {
    $environmentsPath = "workspaces/$($workspaceIds['ING'])/environments"
    $environment = Get-FabricCollection $environmentsPath | Where-Object displayName -EQ $EnvironmentName | Select-Object -First 1
    if (-not $environment) {
        if ($PSCmdlet.ShouldProcess($EnvironmentName, 'Crear Environment en el workspace de ingeniería')) {
            Invoke-Fabric 'Post' $environmentsPath @{ displayName = $EnvironmentName; description = $Description } | Out-Null
            $environment = Get-FabricCollection $environmentsPath | Where-Object displayName -EQ $EnvironmentName | Select-Object -First 1
            Write-Host "Environment creado: $EnvironmentName"
        }
    }
    else {
        Write-Host "Environment existente: $EnvironmentName"
    }
    if ($environment) {
        $updates['ENV_FWK_ID'] = $environment.id
        Set-SparkRuntime $workspaceIds['ING'] $environment.id
    }
}

if ($PSCmdlet.ShouldProcess($EnvFile, "Escribir $($updates.Keys -join ', ')")) {
    Set-DotEnvValues $EnvFile $updates
    Write-Host "IDs escritos en ${EnvFile}: $($updates.Keys -join ', ')"
}
Write-Host 'Siguiente paso: abre los tres workspaces en el portal con esta misma cuenta.'
