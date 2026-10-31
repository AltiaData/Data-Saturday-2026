"""Escritura en Delta según el modo de carga declarado en la configuración."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datafwk.config import MODOS_CARGA
from datafwk.errores import ConfiguracionInvalida

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def escribir(spark: SparkSession, df: DataFrame, ruta: str, modo: str, clave: tuple[str, ...]) -> None:
    if modo not in MODOS_CARGA:
        raise ConfiguracionInvalida(f"modo de carga '{modo}' no es uno de {MODOS_CARGA}")

    from delta.tables import DeltaTable

    if modo == "merge" and DeltaTable.isDeltaTable(spark, ruta):
        condicion = " AND ".join(f"t.{c} = s.{c}" for c in clave)
        (
            DeltaTable.forPath(spark, ruta)
            .alias("t")
            .merge(df.alias("s"), condicion)
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
        return

    modo_spark = "overwrite" if modo in ("overwrite", "merge") else "append"
    df.write.format("delta").mode(modo_spark).option("mergeSchema", "true").save(ruta)
