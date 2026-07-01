from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    lower,
    to_date,
    to_timestamp,
    trim,
    upper,
)

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


def clean_order_items_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de productos por orden usando PySpark."""

    return (
        df.dropDuplicates()
        .withColumn("shipping_limit_date", to_timestamp(col("shipping_limit_date")))
        .withColumn("price", col("price").cast("double"))
        .withColumn("freight_value", col("freight_value").cast("double"))
    )


def clean_order_payments_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de pagos usando PySpark."""

    return (
        df.dropDuplicates()
        .withColumn("payment_type", lower(trim(col("payment_type"))))
        .withColumn("payment_sequential", col("payment_sequential").cast("int"))
        .withColumn("payment_installments", col("payment_installments").cast("int"))
        .withColumn("payment_value", col("payment_value").cast("double"))
    )


def clean_order_reviews_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de reseñas usando PySpark."""

    return (
        df.dropDuplicates()
        .withColumn("review_creation_date", to_date(col("review_creation_date")))
        .withColumn(
            "review_answer_timestamp",
            to_timestamp(col("review_answer_timestamp")),
        )
        .withColumn("review_score", col("review_score").cast("int"))
    )


def clean_products_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de productos usando PySpark."""

    return (
        df.dropDuplicates(["product_id"])
        .withColumn("product_category_name", lower(trim(col("product_category_name"))))
        .withColumn(
            "product_name_lenght",
            col("product_name_lenght").cast("int"),
        )
        .withColumn(
            "product_description_lenght",
            col("product_description_lenght").cast("int"),
        )
        .withColumn("product_photos_qty", col("product_photos_qty").cast("int"))
        .withColumn("product_weight_g", col("product_weight_g").cast("double"))
        .withColumn("product_length_cm", col("product_length_cm").cast("double"))
        .withColumn("product_height_cm", col("product_height_cm").cast("double"))
        .withColumn("product_width_cm", col("product_width_cm").cast("double"))
    )


def clean_sellers_spark(df: DataFrame) -> DataFrame:
    """Limpia la tabla de vendedores usando PySpark."""

    return (
        df.dropDuplicates(["seller_id"])
        .withColumn("seller_city", lower(trim(col("seller_city"))))
        .withColumn("seller_state", upper(trim(col("seller_state"))))
    )


def run_spark_silver_sample(config: dict[str, Any]) -> dict[str, int]:
    """Ejecuta una primera versión Silver con PySpark."""

    bronze_path = Path(config["paths"]["bronze"])
    output_path = Path("data/spark/silver")
    output_path.mkdir(parents=True, exist_ok=True)

    print("Iniciando transformaciones Spark Silver...")

    bronze_tables = {
        "orders": _read_bronze_table(bronze_path, "orders"),
        "customers": _read_bronze_table(bronze_path, "customers"),
        "order_items": _read_bronze_table(bronze_path, "order_items"),
        "order_payments": _read_bronze_table(bronze_path, "order_payments"),
        "order_reviews": _read_bronze_table(bronze_path, "order_reviews"),
        "products": _read_bronze_table(bronze_path, "products"),
        "sellers": _read_bronze_table(bronze_path, "sellers"),
    }

    silver_tables = {
        "orders": clean_orders_spark(bronze_tables["orders"]),
        "customers": clean_customers_spark(bronze_tables["customers"]),
        "order_items": clean_order_items_spark(bronze_tables["order_items"]),
        "order_payments": clean_order_payments_spark(
            bronze_tables["order_payments"],
        ),
        "order_reviews": clean_order_reviews_spark(bronze_tables["order_reviews"]),
        "products": clean_products_spark(bronze_tables["products"]),
        "sellers": clean_sellers_spark(bronze_tables["sellers"]),
    }

    summary = {}

    for table_name, df in silver_tables.items():
        _save_spark_table(df, output_path, table_name)

        total_rows = df.count()
        summary[table_name] = total_rows

        print(f"Spark Silver generado: {table_name} | registros: {total_rows:,}")

    print("Transformaciones Spark Silver finalizadas correctamente.")

    return summary
