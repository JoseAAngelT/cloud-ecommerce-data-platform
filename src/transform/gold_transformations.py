from pathlib import Path
from typing import Any

import pandas as pd


def _read_silver_table(silver_path: Path, table_name: str) -> pd.DataFrame:
    """Lee una tabla desde la capa silver."""

    file_path = silver_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro la tabla silver: {file_path}")

    return pd.read_parquet(file_path)


def _save_gold_table(df: pd.DataFrame, gold_path: Path, table_name: str) -> None:
    """Guarda una tabla en la capa Gold."""

    gold_path.mkdir(parents=True, exist_ok=True)

    output_file = gold_path / f"{table_name}.parquet"
    df.to_parquet(output_file, index=False)


def _build_dim_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Construye la dimension de clientes."""

    columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    dim_customers = customers[columns].copy()
    dim_customers = dim_customers.drop_duplicates(subset=["customer_id"])

    return dim_customers


def build_dim_products(products: pd.DataFrame) -> pd.DataFrame:
    """Construye la dimensión de productos."""

    columns = [
        "product_id",
        "product_category_name",
        "product_category_name_english",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    dim_products = products[columns].copy()
    dim_products = dim_products.drop_duplicates(subset=["product_id"])

    return dim_products


def build_dim_sellers(sellers: pd.DataFrame) -> pd.DataFrame:
    """Construye la dimension de vendedores."""

    columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]

    dim_sellers = sellers[columns].copy()
    dim_sellers = dim_sellers.drop_duplicates(subset=["seller_id"])

    return dim_sellers


def build_dim_date(orders: pd.DataFrame) -> pd.DataFrame:
    """Construye una dimensión de fechas a partir de las órdenes."""

    dates = orders["order_purchase_timestamp"].dropna().dt.date.drop_duplicates()

    dim_date = pd.DataFrame({"date": pd.to_datetime(dates)})
    dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["year_month"] = dim_date["date"].dt.strftime("%Y-%m")

    dim_date = dim_date.sort_values("date").reset_index(drop=True)

    return dim_date


def build_fact_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de hechos de órdenes."""

    fact_orders = orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    ].copy()

    fact_orders["purchase_date_id"] = (
        fact_orders["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype("Int64")
    )

    return fact_orders


def build_fact_order_items(order_items: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de hechos de productos vendidos."""

    fact_order_items = order_items[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ]
    ].copy()

    fact_order_items["total_item_value"] = (
        fact_order_items["price"] + fact_order_items["freight_value"]
    )

    return fact_order_items


def build_fact_payments(order_payments: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de hechos de pagos."""

    fact_payments = order_payments[
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ]
    ].copy()

    return fact_payments


def build_fact_reviews(order_reviews: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de hechos de reseñas."""

    fact_reviews = order_reviews[
        [
            "review_id",
            "order_id",
            "review_score",
            "review_creation_date",
            "review_answer_timestamp",
        ]
    ].copy()

    return fact_reviews


def build_fact_delivery(orders: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de hechos de entregas."""

    fact_delivery = orders[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    ].copy()

    fact_delivery["delivery_days"] = (
        fact_delivery["order_delivered_customer_date"]
        - fact_delivery["order_purchase_timestamp"]
    ).dt.days

    fact_delivery["estimated_delivery_days"] = (
        fact_delivery["order_estimated_delivery_date"]
        - fact_delivery["order_purchase_timestamp"]
    ).dt.days

    fact_delivery["is_late_delivery"] = (
        fact_delivery["order_delivered_customer_date"]
        > fact_delivery["order_estimated_delivery_date"]
    )

    return fact_delivery


def run_gold_transformations(config: dict[str, Any]) -> dict[str, int]:
    """Ejecuta la construcción de tablas Gold."""

    silver_path = Path(config["paths"]["silver"])
    gold_path = Path(config["paths"]["gold"])

    print("Iniciando transformaciones Gold...")

    customers = _read_silver_table(silver_path, "customers")
    products = _read_silver_table(silver_path, "products")
    sellers = _read_silver_table(silver_path, "sellers")
    orders = _read_silver_table(silver_path, "orders")
    order_items = _read_silver_table(silver_path, "order_items")
    order_payments = _read_silver_table(silver_path, "order_payments")
    order_reviews = _read_silver_table(silver_path, "order_reviews")

    gold_tables = {
        "dim_customers": _build_dim_customers(customers),
        "dim_products": build_dim_products(products),
        "dim_sellers": build_dim_sellers(sellers),
        "dim_date": build_dim_date(orders),
        "fact_orders": build_fact_orders(orders),
        "fact_order_items": build_fact_order_items(order_items),
        "fact_payments": build_fact_payments(order_payments),
        "fact_reviews": build_fact_reviews(order_reviews),
        "fact_delivery": build_fact_delivery(orders),
        "agg_sales_by_month": build_agg_sales_by_month(orders, order_items),
        "agg_sales_by_category": build_agg_sales_by_category(order_items, products),
        "agg_delivery_performance": build_agg_delivery_performance(orders),
        "agg_seller_performance": build_agg_seller_performance(order_items, sellers),
        "agg_customer_satisfaction": build_agg_customer_satisfaction(
            orders, order_reviews
        ),
    }

    gold_summary = {}

    for table_name, df in gold_tables.items():
        _save_gold_table(df, gold_path, table_name)
        gold_summary[table_name] = len(df)

        print(f"Gold generado: {table_name} | registros: {len(df):,}")

    print("Transformaciones Gold finalizadas correctamente.")

    return gold_summary


def build_agg_sales_by_month(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> pd.DataFrame:
    """Construye ventas agregadas por mes."""

    sales = order_items.merge(
        orders[["order_id", "order_purchase_timestamp", "order_status"]],
        on="order_id",
        how="left",
    )

    sales["year_month"] = sales["order_purchase_timestamp"].dt.strftime("%Y-%m")
    sales["total_sales"] = sales["price"] + sales["freight_value"]

    agg_sales_by_month = (
        sales.groupby("year_month", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_items=("order_item_id", "count"),
            total_revenue=("price", "sum"),
            total_freight=("freight_value", "sum"),
            total_sales=("total_sales", "sum"),
        )
        .sort_values("year_month")
    )

    return agg_sales_by_month


def build_agg_sales_by_category(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Construye ventas agregadas por categorias de producto."""

    sales = order_items.merge(
        products[
            [
                "product_id",
                "product_category_name_english",
            ]
        ],
        on="product_id",
        how="left",
    )

    sales["product_category_name_english"] = sales[
        "product_category_name_english"
    ].fillna("not_informed")

    sales["total_sales"] = sales["price"] + sales["freight_value"]

    agg_sales_by_category = (
        sales.groupby("product_category_name_english", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_items=("order_item_id", "count"),
            total_revenue=("price", "sum"),
            total_freight=("freight_value", "sum"),
            total_sales=("total_sales", "sum"),
            avg_item_price=("price", "mean"),
        )
        .sort_values("total_sales", ascending=False)
        .reset_index(drop=True)
    )

    return agg_sales_by_category


def build_agg_delivery_performance(orders: pd.DataFrame) -> pd.DataFrame:
    """Construye métricas agregadas de desempeño de entregas."""

    deliveries = orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    ].copy()

    deliveries["delivery_days"] = (
        deliveries["order_delivered_customer_date"]
        - deliveries["order_purchase_timestamp"]
    ).dt.days

    deliveries["is_late_delivery"] = (
        deliveries["order_delivered_customer_date"]
        > deliveries["order_estimated_delivery_date"]
    )

    deliveries["year_month"] = deliveries["order_purchase_timestamp"].dt.strftime(
        "%Y-%m"
    )

    agg_delivery_performance = (
        deliveries.groupby("year_month", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            delivered_orders=("order_delivered_customer_date", "count"),
            avg_delivery_days=("delivery_days", "mean"),
            late_deliveries=("is_late_delivery", "sum"),
        )
        .sort_values("year_month")
    )

    agg_delivery_performance["late_delivery_rate"] = (
        agg_delivery_performance["late_deliveries"]
        / agg_delivery_performance["delivered_orders"]
    )

    return agg_delivery_performance


def build_agg_seller_performance(
    order_items: pd.DataFrame,
    sellers: pd.DataFrame,
) -> pd.DataFrame:
    """Construye métricas de desempeño por vendedor."""

    seller_sales = order_items.merge(
        sellers[["seller_id", "seller_city", "seller_state"]],
        on="seller_id",
        how="left",
    )

    seller_sales["total_sales"] = seller_sales["price"] + seller_sales["freight_value"]

    agg_seller_performance = (
        seller_sales.groupby(
            ["seller_id", "seller_city", "seller_state"],
            as_index=False,
        )
        .agg(
            total_orders=("order_id", "nunique"),
            total_items=("order_item_id", "count"),
            total_revenue=("price", "sum"),
            total_freight=("freight_value", "sum"),
            total_sales=("total_sales", "sum"),
            avg_items_price=("price", "mean"),
        )
        .sort_values("total_sales", ascending=False)
    )

    return agg_seller_performance


def build_agg_customer_satisfaction(
    orders: pd.DataFrame,
    order_reviews: pd.DataFrame,
) -> pd.DataFrame:
    """Construye métricas de satisfacción del cliente por mes."""

    reviews = order_reviews.merge(
        orders[["order_id", "order_purchase_timestamp"]],
        on="order_id",
        how="left",
    )

    reviews["year_month"] = reviews["order_purchase_timestamp"].dt.strftime("%Y-%m")

    agg_customer_satisfaction = (
        reviews.groupby("year_month", as_index=False)
        .agg(
            total_reviews=("review_id", "nunique"),
            avg_review_score=("review_score", "mean"),
            low_score_reviews=("review_score", lambda score: (score <= 2).sum()),
            high_score_reviews=("review_score", lambda score: (score >= 4).sum()),
        )
        .sort_values("year_month")
    )

    agg_customer_satisfaction["low_score_rate"] = (
        agg_customer_satisfaction["low_score_reviews"]
        / agg_customer_satisfaction["total_reviews"]
    )

    agg_customer_satisfaction["high_score_rate"] = (
        agg_customer_satisfaction["high_score_reviews"]
        / agg_customer_satisfaction["total_reviews"]
    )

    return agg_customer_satisfaction
