from pyspark.sql import SparkSession


def create_spark_session(
    app_name: str = "cloud-ecommerce-data-platform",
) -> SparkSession:
    """Crea una sesión local de Spark."""

    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
