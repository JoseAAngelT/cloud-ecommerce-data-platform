from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, date_format, year

from src.spark.spark_session import create_spark_session


def _read_spark_silver_table(silver_path: Path, table_name: str) -> DataFrame:
    """Lee una tabla Silver generada por Spark."""

    spark = create_spark_session()
    table_path = silver_path / table_name

    if not table_path.exists():
        raise FileNotFoundError(f"No se encontró la tabla Spark Silver: {table_path}")

    return spark.read.parquet(str(table_path))


def _save_spark_gold_table(df: DataFrame, output_path: Path, table_name: str) -> None:
    """Guarda una tabla Gold generada por Spark."""

    table_path = output_path / table_name

    df.write.mode("overwrite").parquet(str(table_path))


def build_dim_customers_spark(customers: DataFrame) -> DataFrame:
    """Construye la dimensión de clientes usando PySpark."""

    return customers.select(
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ).dropDuplicates(["customer_id"])


def build_dim_products_spark(products: DataFrame) -> DataFrame:
    """Construye la dimensión de productos usando PySpark."""

    return products.select(
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ).dropDuplicates(["product_id"])


def build_dim_sellers_spark(sellers: DataFrame) -> DataFrame:
    """Construye la dimensión de vendedores usando PySpark."""

    return sellers.select(
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ).dropDuplicates(["seller_id"])


def build_fact_orders_spark(orders: DataFrame) -> DataFrame:
    """Construye la tabla de hechos de órdenes usando PySpark."""

    return (
        orders.select(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        )
        .withColumn(
            "purchase_date_id",
            date_format(col("order_purchase_timestamp"), "yyyyMMdd").cast("int"),
        )
        .withColumn("purchase_year", year(col("order_purchase_timestamp")))
        .dropDuplicates(["order_id"])
    )


def run_spark_gold_sample(config: dict[str, Any]) -> dict[str, int]:
    """Ejecuta una primera versión Gold con PySpark."""

    silver_path = Path("data/spark/silver")
    output_path = Path("data/spark/gold")
    output_path.mkdir(parents=True, exist_ok=True)

    print("Iniciando transformaciones Spark Gold...")

    customers = _read_spark_silver_table(silver_path, "customers")
    products = _read_spark_silver_table(silver_path, "products")
    sellers = _read_spark_silver_table(silver_path, "sellers")
    orders = _read_spark_silver_table(silver_path, "orders")

    gold_tables = {
        "dim_customers": build_dim_customers_spark(customers),
        "dim_products": build_dim_products_spark(products),
        "dim_sellers": build_dim_sellers_spark(sellers),
        "fact_orders": build_fact_orders_spark(orders),
    }

    summary = {}

    for table_name, df in gold_tables.items():
        _save_spark_gold_table(df, output_path, table_name)

        total_rows = df.count()
        summary[table_name] = total_rows

        print(f"Spark Gold generado: {table_name} | registros: {total_rows:,}")

    print("Transformaciones Spark Gold finalizadas correctamente.")

    return summary
