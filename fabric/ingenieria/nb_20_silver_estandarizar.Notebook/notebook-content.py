# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_20_silver_estandarizar
# Bronze → silver: snake_case, contrato de datos, deduplicación por clave y carga según `modo_carga`.
# 
# Las filas que no cumplen el contrato van a `_cuarentena_<tabla>` con todos sus motivos.
# Cada ejecución queda en `lh_silver.fwk_ejecuciones` y debe reconciliar: leídas = escritas + rechazadas.

# PARAMETERS CELL ********************

entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "ventas"
fuente = "pedidos"
batch_id = ""   # vacío = reprocesar todo bronze (el merge lo hace idempotente)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto
from datafwk.silver import a_silver

ctx = cargar_contexto(entorno, workspace_datos, dominio)
ejecucion = a_silver(spark, ctx.fuente(fuente), ctx.contrato(fuente), ctx.entorno, batch_id or None)
print(
    f"{ejecucion.estado}: {ejecucion.filas_escritas} válidas, {ejecucion.filas_rechazadas} a cuarentena "
    f"en silver.{ejecucion.tabla}"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if ejecucion.estado != "ok":
    raise RuntimeError(f"La ejecución terminó en estado '{ejecucion.estado}'. Revisa fwk_ejecuciones.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
