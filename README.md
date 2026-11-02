# Data Saturday 2026 · Edición para alumnos

Guía práctica para seguir el workshop de cuatro horas: proyecto greenfield, calidad, incremental y SCD2.

## Empieza aquí

1. Prepara tu equipo con [Antes de la sesión](docs/workshop/01_antes-de-la-sesion.md).
2. Completa con el instructor la [ficha del laboratorio](docs/workshop/00_ficha-laboratorio.md).
3. Sigue [Las demos paso a paso](docs/workshop/02_seguir-las-demos.md).
4. Consulta la [validación de esta edición](docs/workshop/03_validacion-edicion.md).

**Modalidad guiada:** generas y cambias tu proyecto local; el instructor ejecuta las cargas y muestra los resultados.
**Laboratorio individual:** ejecutas también en Fabric si tienes asignados recursos y una copia SQL propios.

No publiques YAML, cambies SQL ni ejecutes cargas contra los recursos compartidos del instructor.
Dos participantes con diferentes `batch_id` siguen escribiendo las mismas tablas si comparten workspace.

## Qué vas a construir

| Demo | Cambio observable |
|---|---|
| Greenfield | Proyecto independiente generado desde esta plantilla |
| Completa / Q1 | Lectura SQL directa; datos válidos y rechazos separados |
| Q2 / Q3 / Q4 | Nuevas condiciones, fallo esperado y recuperación |
| Incremental | Lectura por `updated_at` y reintentos sin duplicados |
| SCD2 | Ciudad pasa de sobrescritura a historia Barcelona→Valencia→Barcelona |
| Consumo | Diferencia entre clientes actuales y versiones históricas |
| Revisión | Contratos, catálogo, pruebas y límites de recuperación |

El framework completo está incluido para poder explorar y ejecutar sus pruebas. Los checkpoints son material de apoyo:
aplicarlos no equivale a haber publicado ni ejecutado una demo.

## Procedencia y documentación técnica

Copia independiente de `f0f2551` de [AltiaData/DataSaturday2026](https://github.com/AltiaData/DataSaturday2026),
biblioteca `0.2.0`. Conserva el historial y no tiene remoto configurado.
La generación greenfield renueva los identificadores de Fabric; clonar este repo no los renueva.

- [README original](README-framework.md)
- [Convenciones](docs/convenciones.md) · [Glosario](docs/glosario.md)
- [Runbook técnico](docs/runbooks/workshop-evolutivo.md)
- [Tests y límites de la entrega](docs/validacion-workshop.md)

Las credenciales, workspaces, base SQL, Environment y el informe no se crean al copiar este repo.
