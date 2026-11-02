# Antes de la sesión · Alumnos

## 1. Qué necesitas

Para la modalidad guiada: esta copia, Git, PowerShell 7 y Python 3.11/3.12, con VS Code o editor equivalente.
El instructor mostrará las ejecuciones de SQL/Fabric. No necesitas permisos cloud para generar y revisar el producto local.

Para ejecutar pruebas Spark en tu equipo: Java 17 y las dependencias dev. En Windows se necesitan las utilidades
nativas Hadoop para los escenarios Delta. El devcontainer Linux incluido evita esa preparación específica Windows.
Instalar y descargar antes del evento; no dedicar los 35 minutos de greenfield a preparar Spark.

Para laboratorio individual: el instructor debe asignarte base SQL, workspaces, Environment publicado, identidad
y permisos propios. El repo no crea esos recursos al abrirlo.

## 2. Prepara Python en la copia entregada

PowerShell, desde la raíz de la edición de alumnos:

~~~powershell
$Plantilla = (Get-Location).Path
py -3.12 -m venv .venv
$PythonPlantilla = Join-Path $Plantilla '.venv\Scripts\python.exe'
$env:PATH = "$Plantilla\.venv\Scripts;$env:PATH"
& $PythonPlantilla -m pip install -e '.[dev]'
git --version
& $PythonPlantilla -c "import datafwk; print(datafwk.__version__)"
~~~

Con Python 3.11 sustituir `py -3.12` por `py -3.11`. Si el entorno ya existe, comprobarlo y reutilizarlo.
**Esperado:** Git disponible y datafwk 0.2.0. Las herramientas y virtualenv del instructor no están incluidas.

Para publicar en tu laboratorio individual, además:

~~~powershell
& $PythonPlantilla -m pip install -e '.[deploy]'
az login --tenant '<tenant-asignado>'
~~~

En el devcontainer, instalar con `python -m pip install -e '.[dev]'` y usar `python` en lugar de la ruta
`.venv\Scripts\python.exe`. El resto de comandos PowerShell usan rutas Windows: adaptar las rutas al montaje Linux.

## 3. Recibe la ficha y elige tu nombre de proyecto

Completar [ficha del laboratorio](00_ficha-laboratorio.md).
En modo guiado, los campos cloud pertenecen a la demostración y se anotan para entenderla, no para publicar en ellos.

El nombre del proyecto debe tener 3–40 caracteres, comenzar por letra minúscula y usar letras minúsculas,
dígitos o guiones. Ejemplo: `fsh-equipo01`.
La carpeta de destino debe ser nueva, hermana de la plantilla, nunca dentro de ella.

No crear aún el producto: lo haremos en la demo 1. Los ocho IDs de Fabric se renuevan con el generador,
no con una copia manual o git clone.

## 4. Lee el contexto

- [Convenciones](../convenciones.md): dónde vive cada pieza.
- [Glosario](../glosario.md): las definiciones de negocio se acuerdan.
- [ADR de evolución](../adr/0002-evolucion-cargas-calidad-historia.md): extracción, calidad e historia.
- [Demos](02_seguir-las-demos.md): comandos y preguntas del recorrido.

No es necesario memorizar el motor. Localiza:
`config/fuentes/`, `contracts/`, `config/modelos/`, `src/datafwk/` y `templates/workshop/`.

### Herramientas de validación en Windows

Para los hooks Terraform en Windows, Git Bash debe estar en el PATH:

~~~powershell
$GitRoot = Split-Path -Parent (Split-Path -Parent (Get-Command git).Source)
$env:PATH = "$GitRoot\bin;$GitRoot\usr\bin;$env:PATH"
Get-Command bash
~~~

Si pytest informa de acceso denegado a `pytest-of-<usuario>`, usar una carpeta temporal nueva dentro del producto:

~~~powershell
$TmpPruebas = Join-Path $Proyecto ('.herramientas/pytest-' + (Get-Date -Format 'yyyyMMddHHmmss'))
& $Python -m pytest --delta -q --basetemp $TmpPruebas
~~~

Este comando se ejecuta después de preparar `$Proyecto` y `$Python`. No modificar permisos de carpetas temporales
de otros procesos. Un bloqueo de Control de aplicaciones de Windows debe resolverlo el administrador o validarse
en el devcontainer; no desactivar hooks para obtener un resultado verde.

## 5. Antes de comenzar

- [ ] Puedo abrir esta copia y ejecutar Python.
- [ ] Entiendo si mi modalidad es guiada o individual.
- [ ] Tengo un nombre y una carpeta nueva para greenfield.
- [ ] Si ejecuto Spark local, Java/runtime están probados.
- [ ] Si publico en cloud, tengo recursos aislados y conectividad ya comprobada.
- [ ] Sé que los cambios de SQL los coordina el instructor.

Si no tienes laboratorio individual, sigue todos los cambios locales y anota los resultados mostrados.
Una carga observada en pantalla no es una ejecución propia; registra esa diferencia en tu ficha.
