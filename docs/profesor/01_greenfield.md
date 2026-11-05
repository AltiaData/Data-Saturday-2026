# Demo 1 · Generar un proyecto greenfield

Minutos 15–50 (35 min). Guía del alumnado: [Demo 1](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-01` (la plantilla).

## Objetivo y mensajes clave

- Crear un producto independiente exige identificadores de items nuevos (`logicalId`), configuración propia y secretos
  locales. El generador no copia `.git`, entornos virtuales, credenciales ni CSV ya mutados.
- Contratos antes que código: el proyecto nace con los contratos Q1 y tipo1 y las fuentes CSV en extracción completa.
- Los nombres de los workspaces viven en `config/entornos/` y `parameter.yml`, nunca en el código.
- Publicar recursos no es desplegar todo: no se publica analítica ni se ejecuta `desplegar.py` completo, porque el
  workshop crea la dimensión del taller y no las tablas de ventas de los ejemplos genéricos.

## Qué enseñar en pantalla

- `escenario.json` (en `data/laboratorio/`): cliente `C0001` (Sevilla) y las cuatro devoluciones elegidas.
- El diff entre la plantilla y el proyecto generado: `.platform` con `logicalId` nuevos, `config/entornos/dev.yml` y
  `fabric/ingenieria/parameter.yml` con los nombres propios, y ausencia de `.env.instructor.example`. Con las ramas:
  `git diff --stat alumno-99/demo-01 alumno-99/demo-02`.
- `config/fuentes/crm.yml`: `fecha_cambio` como marca CRM.
- En Fabric, tras publicar: `lh_bronze`, `lh_silver`, `lh_gold` en datos; cinco notebooks en ingeniería; `env_fwk`
  con el wheel 0.3.0; YAML en `lh_bronze/Files/_framework` y CSV en `Files/landing`.

## Comandos

Desde la copia entregada, con `$Python`, `$Plantilla` y `.env.alumno` de la preparación. Sustituir `fsh-alumno01` por
el proyecto propio en los dos comandos y en `.env.alumno`; el destino debe ser nuevo.

```powershell
$Producto = Join-Path (Split-Path $Plantilla -Parent) 'fsh-alumno01-lab'
& $Python scripts/crear_proyecto.py $Producto --proyecto fsh-alumno01
Copy-Item (Join-Path $Plantilla '.env.alumno') (Join-Path $Producto '.env.alumno')
Set-Location $Producto
& $Python -m pip install -e '.[dev,deploy]'
git init -b main
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
& $Python -m scripts.laboratorio checkpoint --paso base --env-file .env.alumno
& $Python -m scripts.modificar_csv preparar
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py

& $Python -m scripts.laboratorio lakehouses --env-file .env.alumno
& $Python -m build --wheel
& $Python -m scripts.laboratorio wheel --env-file .env.alumno
& $Python -m scripts.laboratorio notebooks --env-file .env.alumno
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

Después, en Fabric: vincular **cada uno** de los cinco notebooks a `env_fwk`, guardar y detener sesiones anteriores.

## Resultado esperado

- Contratos Q1 y tipo1, fuentes CSV en completa, `logicalId` nuevos y dos CSV de trabajo.
- Tres lakehouses sin esquemas: `LAKEHOUSE_ESQUEMA` vacío y `config/entornos/dev.yml` sin clave `esquema`. En el SQL
  analytics endpoint las tablas aparecerán igualmente bajo `dbo`.
- Cinco notebooks vinculados a `env_fwk` con `datafwk` 0.3.0.

## Tiempo medido

Parte local 33 s. Publicación unos 7 min: `lakehouses` 24 s, `build` 5 s, `wheel` 354 s, `notebooks` 11 s, `config`
15 s. A eso se suma la vinculación manual de los cinco notebooks en el portal. Margen holgado si la preparación está
hecha: aprovechar los 6 min del wheel para explicar contratos y convenciones.

## Preguntas frecuentes previsibles

- **¿Por qué no copiar el repositorio sin más?** Porque los `logicalId` se repetirían entre productos y se arrastrarían
  `.git`, dotenv y CSV mutados; el generador crea identificadores nuevos y excluye todo eso.
- **¿Por qué el esquema vacío si el endpoint muestra `dbo`?** Los lakehouses que publica el repositorio no tienen
  esquemas; con `dbo` las tablas irían a `Tables/dbo/` y no aparecerían en el endpoint (hallazgo 16).
- **¿Se puede vincular el Environment una sola vez?** Sí: *Set default environment* con `env_fwk` en la configuración
  del workspace, según la preparación del alumnado. Si no, notebook a notebook.
- **¿Por qué no `desplegar.py`?** Publicaría analítica y ejemplos genéricos que no forman parte del taller.

## Incidencias reales del diario

- Hallazgo 15: el wheel tarda unos 6 minutos (354 s) de los 35 del bloque. Publicarlo en la preparación previa está
  pendiente de decisión.
- Hallazgo 14 (corregido en `setup`): `laboratorio datos` fallaba con `FriendlyNameSupportDisabled`. Si alguien trae una
  copia antigua del repositorio, actualizarla.
- Hallazgo 16 (corregido): `LAKEHOUSE_ESQUEMA=dbo` por defecto. Con un `.env.alumno` creado antes de la corrección,
  vaciar el valor y repetir `configurar` y `config`.
- Hallazgos 9 y 8: si el Environment está en Runtime 2.0, cambiarlo a 1.3 **antes** de publicar el wheel; cambiarlo
  después obliga a publicar de nuevo.
- Hallazgo 7: workspaces creados desde una CLI con otra cuenta no son visibles en el portal.

## Plan B

Si el greenfield no sale (por ejemplo, error en `crear_proyecto.py` o en la instalación del destino), la persona sigue
desde la copia entregada con el proyecto ya generado. Procedimiento común en el [README](README.md#plan-b-común-incorporarse-en-la-demo-nn):

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-02
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
& $Python -m scripts.modificar_csv preparar
& $Python scripts/validar_contratos.py
```

Después, la publicación de esta demo (`lakehouses`, `build`, `wheel`, `notebooks`, `config`, `datos`) y la
vinculación de los notebooks. Lotes previos en Fabric: ninguno. No aplicar `checkpoint base`: la rama `demo-02` ya lo
lleva aplicado.
