from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lower, to_timestamp, trim, upper

from src.spark.spark_session import create_spark_session


def _read_bronze_table(bronze_path: Path, table_name: str) -> DataFrame:
    """Lee una tabla Bronze en formato Parquet usando Spark."""

    spark = create_spark_session()
    file_path = bronze_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró la tabla Bronze: {file_path}")

    return spark.read.parquet(str(file_path))


def _save_spark_table(df: DataFrame, output_path: Path, table_name: str) -> None:
    """Guarda una tabla procesada por Spark en formato Parquet."""

    table_path = output_path / table_name

    df.write.mode("overwrite").parquet(str(table_path))


def clean_orders_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de órdenes usando PySpark."""

    return (
        df.dropDuplicates(["order_id"])
        .withColumn("order_status", lower(trim(col("order_status"))))
        .withColumn(
            "order_purchase_timestamp",
            to_timestamp(col("order_purchase_timestamp")),
        )
        .withColumn("order_approved_at", to_timestamp(col("order_approved_at")))
        .withColumn(
            "order_delivered_carrier_date",
            to_timestamp(col("order_delivered_carrier_date")),
        )
        .withColumn(
            "order_delivered_customer_date",
            to_timestamp(col("order_delivered_customer_date")),
        )
        .withColumn(
            "order_estimated_delivery_date",
            to_timestamp(col("order_estimated_delivery_date")),
        )
    )


def clean_customers_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de clientes usando PySpark."""

    return (
        df.dropDuplicates(["customer_id"])
        .withColumn("customer_city", lower(trim(col("customer_city"))))
        .withColumn("customer_state", upper(trim(col("customer_state"))))
    )


def run_spark_silver_sample(config: dict[str, Any]) -> dict[str, int]:
    """Ejecuta una primera versión Silver con PySpark."""

    bronze_path = Path(config["paths"]["bronze"])
    output_path = Path("data/spark/silver")
    output_path.mkdir(parents=True, exist_ok=True)

    print("Iniciando transformaciones Spark Silver...")

    orders = _read_bronze_table(bronze_path, "orders")
    customers = _read_bronze_table(bronze_path, "customers")

    silver_orders = clean_orders_spark(orders)
    silver_customers = clean_customers_spark(customers)

    _save_spark_table(silver_orders, output_path, "orders")
    _save_spark_table(silver_customers, output_path, "customers")

    summary = {
        "orders": silver_orders.count(),
        "customers": silver_customers.count(),
    }

    for table_name, total_rows in summary.items():
        print(f"Spark Silver generado: {table_name} | registros: {total_rows:,}")

    print("Transformaciones Spark Silver finalizadas correctamente.")

    return summary
