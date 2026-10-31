import pytest


@pytest.fixture(scope="session")
def spark():
    pyspark = pytest.importorskip("pyspark", reason="instala las dependencias de desarrollo: pip install -e '.[dev]'")
    sesion = (
        pyspark.sql.SparkSession.builder.master("local[1]")
        .appName("tests-datafwk")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    yield sesion
    sesion.stop()
