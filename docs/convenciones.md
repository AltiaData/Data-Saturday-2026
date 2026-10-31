# Convenciones

Las convenciones se deciden una vez y se cumplen siempre. Cambiar una requiere un ADR en `docs/adr/`.

## Workspaces
`<proyecto>-<función>-<entorno>`

| Función | Contenido | Quién escribe |
|---|---|---|
| `datos` | Lakehouses `lh_bronze`, `lh_silver`, `lh_gold` | Solo la identidad de los pipelines |
| `ing` | Notebooks, pipelines, Environment `env_fwk` | Ingeniería de datos |
| `ana` | Modelos semánticos e informes | Analítica / BI |

Entornos: `dev`, `test`, `prod`. Además, cada persona trabaja en un workspace de feature
(`<proyecto>-ing-feat-<iniciales>`) creado con *branch out* desde su rama.

## Lakehouses y tablas
- Capas: `lh_bronze` (raw, append-only), `lh_silver` (limpio y conforme a contrato), `lh_gold` (modelo de consumo)
- Tablas silver: `<entidad>` en singular de negocio (`pedidos`, `clientes`)
- Tablas gold: `fact_<hecho>_<grano>` y `dim_<entidad>`
- Cuarentena: `_cuarentena_<tabla>` en la misma capa
- Auditoría del framework: `fwk_ejecuciones` en silver
- Ficheros de entrada: `lh_bronze/Files/landing/<dominio>/<fuente>/`
- Configuración publicada: `lh_bronze/Files/_framework/`

## Columnas
- `snake_case`, sin tildes ni ñ, en español de negocio
- Técnicas con prefijo `_`: `_ingested_at`, `_source`, `_batch_id`, `_motivo_rechazo`
- Fechas `fecha_<qué>`, importes `importe_<qué>`, indicadores `es_<qué>` o `tiene_<qué>`, identificadores `id_<entidad>`

## Notebooks y pipelines
- `nb_<nn>_<capa>_<propósito>`: `10` bronze, `20` silver, `30` gold, `90` operación
- `pl_<propósito>` para pipelines de orquestación

## Código
- Toda la lógica en `src/datafwk/`; los notebooks solo orquestan
- Ramas: `feat/<descripción>`, `fix/<descripción>`; PR obligatorio contra `main`
- Commits en español, en imperativo: `Añade fuente devoluciones`
