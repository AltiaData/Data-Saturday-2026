"""Bronze -> silver: estandarizar, aplicar contrato, deduplicar y cargar. Lo que no cumple va a cuarentena."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk import rutas
from datafwk.auditoria import Ejecucion, registrar_ejecucion
from datafwk.calidad import aplicar_contrato
from datafwk.config import Contrato, Entorno, Fuente
from datafwk.errores import ContratoIncumplido
from datafwk.escritura import escribir
from datafwk.estandarizar import deduplicar, renombrar_columnas

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def a_silver(
    spark: SparkSession,
    fuente: Fuente,
    contrato: Contrato,
    entorno: Entorno,
    batch_id: str | None = None,
) -> Ejecucion:
    """Sin batch_id reprocesa todo bronze; el merge por clave lo hace idempotente."""
    from pyspark.sql import functions as F

    ejecucion = Ejecucion(
        batch_id=batch_id or "completo",
        entorno=entorno.nombre,
        capa="silver",
        fuente=fuente.nombre,
        tabla=fuente.tabla_silver,
        inicio=datetime.now(timezone.utc),
    )
    try:
        origen = spark.read.format("delta").load(rutas.tabla(entorno, "bronze", fuente.tabla_bronze))
        if batch_id:
            origen = origen.where(F.col("_batch_id") == batch_id)

        validas, rechazadas = aplicar_contrato(renombrar_columnas(origen), contrato)
        validas, rechazadas = validas.cache(), rechazadas.cache()
        n_validas, n_rechazadas = validas.count(), rechazadas.count()

        if n_rechazadas and contrato.politica_rechazo == "fallar":
            raise ContratoIncumplido(f"{contrato.tabla}: {n_rechazadas} filas incumplen el contrato")

        ejecucion.filas_leidas = n_validas + n_rechazadas
        ejecucion.filas_rechazadas = n_rechazadas
        validas = deduplicar(validas, contrato.clave, orden="_ingested_at")
        ejecucion.filas_escritas = n_validas  # los duplicados por clave se consolidan, no se pierden

        escribir(spark, validas, rutas.tabla(entorno, "silver", fuente.tabla_silver), fuente.modo_carga, contrato.clave)
        if n_rechazadas:
            rechazadas.write.format("delta").mode("append").option("mergeSchema", "true").save(
                rutas.cuarentena(entorno, "silver", fuente.tabla_silver)
            )
        ejecucion.cerrar()
    except Exception as exc:
        ejecucion.cerrar("error", str(exc)[:2000])
        raise
    finally:
        registrar_ejecucion(spark, ejecucion, rutas.auditoria(entorno))
    return ejecucion
