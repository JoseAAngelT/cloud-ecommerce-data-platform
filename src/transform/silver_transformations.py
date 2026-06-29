from pathlib import Path
from typing import Any

import pandas as pd


def _read_bronze_table(bronze_path: Path, table_name: str) -> pd.DataFrame:
    """Lee una tabla desde la capa Bronze."""

    file_path = bronze_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro la tabla Bronze: {file_path}")

    return pd.read_parquet(file_path)


def _save_silver_table(df: pd.DataFrame, silver_path: Path, table_name: str) -> None:
    """Guarda una tabla limpia en la capa Silver."""

    silver_path.mkdir(parents=True, exist_ok=True)

    output_file = silver_path / f"{table_name}.parquet"
    df.to_parquet(output_file, index=False)


def _to_datetime(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convierte columnas a tipo de fecha cuando existen en el DataFrame."""

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    return df


def _to_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convierte columnas a tipo númerico cuando existen."""

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def _normalize_text(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Estandariza columnas de texto en minúsculas y sin espacios sobrantes."""

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip().str.lower()

    return df


def _normalize_state(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Estandariza columnas de estado en mayúsculas."""

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip().str.upper()

    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de geolocalización."""

    df = df.copy()

    df = df.drop_duplicates()
    df = _to_numeric(
        df,
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
        ],
    )
    df = _normalize_text(df, ["geolocation_city"])
    df = _normalize_state(df, ["geolocation_state"])

    return df


def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de geolocalización."""

    df = df.copy()

    df = df.drop_duplicates()
    df = _to_numeric(
        df,
        [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
        ],
    )

    df = _normalize_text(df, ["geolocation_city"])
    df = _normalize_state(df, ["geolocation_state"])

    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de órdenes."""

    df = df.copy()

    df = df.drop_duplicates(subset=["order_id"])
    df = _normalize_text(df, ["order_status"])
    df = _to_datetime(
        df,
        [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )

    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de productos vendidos por orden."""

    df = df.copy()

    df = df.drop_duplicates()
    df = _to_datetime(df, ["shipping_limit_date"])
    df = _to_numeric(
        df,
        [
            "order_item_id",
            "price",
            "freight_value",
        ],
    )

    return df


def clean_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de pagos."""

    df = df.copy()
    df = _normalize_text(df, ["payment_type"])
    df = _to_numeric(
        df,
        [
            "payment_sequential",
            "payment_installments",
            "payment_value",
        ],
    )

    return df


def clean_order_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de reseñas."""

    df = df.copy()

    df = df.drop_duplicates(subset=["review_id", "order_id"])
    df = _to_datetime(
        df,
        [
            "review_creation_date",
            "review_answer_timestamp",
        ],
    )
    df = _to_numeric(df, ["review_score"])

    return df


def clean_products(
    products: pd.DataFrame,
    category_translation: pd.DataFrame,
) -> pd.DataFrame:
    """Limpia la tabla de productos y agrega la categoria traducida."""

    products = products.copy()
    category_translation = category_translation.copy()

    products = products.drop_duplicates(subset=["product_id"])

    products = _normalize_text(products, ["product_category_name"])
    category_translation = _normalize_text(
        category_translation,
        [
            "product_category_name",
            "product_category_name_english",
        ],
    )

    products = _to_numeric(
        products,
        [
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_lenght_cm",
            "product_height_cm",
            "product_width_cm",
        ],
    )

    products = products.merge(
        category_translation,
        on="product_category_name",
        how="left",
    )

    return products


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de vendedores."""

    df = df.copy()

    df = df.drop_duplicates(subset=["seller_id"])
    df = _normalize_text(df, ["seller_city"])
    df = _normalize_state(df, ["seller_state"])

    return df


def clean_product_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la tabla de traducción de categorías."""

    df = df.copy()

    df = df.drop_duplicates(subset=["product_category_name"])
    df = _normalize_text(
        df,
        [
            "product_category_name",
            "product_caregory_name_english",
        ],
    )

    return df


def run_silver_transformations(config: dict[str, Any]) -> dict[str, int]:
    """Ejecuta las transformaciones de la capa Silver."""

    bronze_path = Path(config["paths"]["bronze"])
    silver_path = Path(config["paths"]["silver"])

    print("Iniciando transformaciones Silver...")

    customers = _read_bronze_table(bronze_path, "customers")
    geolocation = _read_bronze_table(bronze_path, "geolocation")
    orders = _read_bronze_table(bronze_path, "orders")
    order_items = _read_bronze_table(bronze_path, "order_items")
    order_payments = _read_bronze_table(bronze_path, "order_reviews")
    order_reviews = _read_bronze_table(bronze_path, "order_reviews")
    products = _read_bronze_table(bronze_path, "products")
    sellers = _read_bronze_table(bronze_path, "sellers")
    category_translation = _read_bronze_table(
        bronze_path, "product_category_translation"
    )

    silver_tables = {
        "customers": clean_customers(customers),
        "geolocation": clean_geolocation(geolocation),
        "orders": clean_orders(orders),
        "order_items": clean_order_items(order_items),
        "order_payments": clean_order_payments(order_payments),
        "order_reviews": clean_order_reviews(order_reviews),
        "products": clean_products(products, category_translation),
        "sellers": clean_sellers(sellers),
        "product_category_translation": clean_product_category_translation(
            category_translation,
        ),
    }

    transformation_summary = {}

    for table_name, df in silver_tables.items():
        _save_silver_table(df, silver_path, table_name)
        transformation_summary[table_name] = len(df)

        print(f"Silver generado: {table_name} | registros: {len(df):,}")

    print("Transformaciones Silver finalizadas correctamente.")

    return transformation_summary
