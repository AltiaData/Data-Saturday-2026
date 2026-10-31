"""Landing -> bronze. Bronze es append-only: guarda lo que llegó, tal como llegó, con trazabilidad."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk import rutas
from datafwk.auditoria import Ejecucion, anadir_columnas_tecnicas, nuevo_batch_id, registrar_ejecucion
from datafwk.config import Entorno, Fuente

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def a_bronze(spark: SparkSession, fuente: Fuente, entorno: Entorno, batch_id: str | None = None) -> Ejecucion:
    batch_id = batch_id or nuevo_batch_id()
    destino = rutas.tabla(entorno, "bronze", fuente.tabla_bronze)
    ejecucion = Ejecucion(
        batch_id=batch_id,
        entorno=entorno.nombre,
        capa="bronze",
        fuente=fuente.nombre,
        tabla=fuente.tabla_bronze,
        inicio=datetime.now(timezone.utc),
    )
    try:
        df = (
            spark.read.format(fuente.formato)
            .options(**fuente.opciones_lectura)
            .load(rutas.ficheros(entorno, "bronze", fuente.ruta_landing))
        )
        df = anadir_columnas_tecnicas(df, fuente.nombre, batch_id)
        ejecucion.filas_leidas = ejecucion.filas_escritas = df.count()
        df.write.format("delta").mode("append").option("mergeSchema", "true").save(destino)
        ejecucion.cerrar()
    except Exception as exc:
        ejecucion.cerrar("error", str(exc)[:2000])
        raise
    finally:
        registrar_ejecucion(spark, ejecucion, rutas.auditoria(entorno))
    return ejecucion
