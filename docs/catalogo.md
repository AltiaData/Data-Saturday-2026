# Catálogo de datos

> Generado por `scripts/generar_catalogo.py` desde `contracts/`. No editar a mano.

## silver

### `clientes`

Un cliente por fila, con su segmento comercial vigente.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** id_cliente · **Si incumple el contrato:** cuarentena

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `id_cliente` | string | no |  | Identificador único del cliente |
| `fecha_alta` | date | no |  | Fecha de alta como cliente |
| `segmento` | string | sí | particular, profesional, empresa | Segmento comercial |
| `provincia` | string | sí |  | Provincia de residencia o domicilio fiscal |
| `acepta_comunicaciones` | boolean | no |  | Consentimiento de comunicaciones comerciales |

### `pedidos`

Un pedido de cliente por fila, en cualquier canal de venta.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** id_pedido · **Si incumple el contrato:** cuarentena

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `id_pedido` | string | no |  | Identificador del pedido en el sistema origen |
| `id_cliente` | string | no |  | Cliente que hace el pedido |
| `fecha_pedido` | date | no |  | Fecha en que se confirma el pedido |
| `canal` | string | no | tienda, web, app | Canal de venta |
| `importe_total` | decimal(12,2) | no |  | Importe con impuestos, en euros |
| `estado` | string | sí | confirmado, enviado, entregado, cancelado | Estado actual |

**Reglas:**

- `importe_no_negativo`: `importe_total >= 0` — Un pedido no puede tener importe negativo; las devoluciones van en su propia tabla
- `fecha_no_futura`: `fecha_pedido <= current_date()` — Ningún pedido puede estar fechado en el futuro

## gold

### `fact_ventas_diarias`

Ventas agregadas por día y canal. Base de los informes de ventas.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** fecha, canal · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `fecha` | date | no |  | Día natural |
| `canal` | string | no | tienda, web, app | Canal de venta |
| `num_pedidos` | int | no |  | Pedidos no cancelados del día |
| `importe_ventas` | decimal(14,2) | no |  | Ver 'Ventas netas' en docs/glosario.md |

**Reglas:**

- `pedidos_positivos`: `num_pedidos > 0`
