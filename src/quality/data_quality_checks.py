import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def _read_table(base_path: Path, table_name: str) -> pd.DataFrame:
    """Lee una tabla Parquet desde una capa del pipeline."""

    file_path = base_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró la tabla: {file_path}")

    return pd.read_parquet(file_path)


def _add_check(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    check_name: str,
    passed: bool,
    details: str,
) -> None:
    """Agrega el resultado de una validación al reporte."""

    checks.append(
        {
            "layer": layer,
            "table": table,
            "check_name": check_name,
            "passed": passed,
            "details": details,
        }
    )


def _check_not_empty(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    df: pd.DataFrame,
) -> None:
    """Valida que una tabla no esté vacia."""

    passed = len(df) > 0
    details = f"rows={len(df):,}"

    _add_check(checks, layer, table, "table_not_empty", passed, details)


def _check_required_columns(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    df: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Valida que existan columnas obligatorias."""

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    passed = len(missing_columns) == 0
    details = "ok" if passed else f"missing_columns={missing_columns}"

    _add_check(checks, layer, table, "required_columns", passed, details)


def _check_no_nulls(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """Valida que columnas críticas no tengan valores nulos."""

    existing_columns = [column for column in columns if column in df.columns]
    null_counts = df[existing_columns].isna().sum().to_dict()

    failed_columns = {
        column: int(null_count)
        for column, null_count in null_counts.items()
        if null_count > 0
    }

    passed = len(failed_columns) == 0
    details = "ok" if passed else f"null_counts={failed_columns}"

    _add_check(checks, layer, table, "critical_columns_without_nulls", passed, details)


def _check_non_negative_values(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """Valida que columnas númericas no tengan valores negativos."""

    invalid_counts = {}

    for column in columns:
        if column in df.columns:
            invalid_count = int((df[column] < 0).fillna(False).sum())

            if invalid_count > 0:
                invalid_counts[column] = invalid_count

    passed = len(invalid_counts) == 0
    details = "ok" if passed else f"negative_values={invalid_counts}"

    _add_check(checks, layer, table, "non_negative_values", passed, details)


def _check_values_between(
    checks: list[dict[str, Any]],
    layer: str,
    table: str,
    df: pd.DataFrame,
    column: str,
    min_value: int,
    max_value: int,
) -> None:
    """Valida que una columna esté dentro de un rango esperado."""

    if column not in df.columns:
        _add_check(
            checks,
            layer,
            table,
            f"{column}_between_{min_value}_and_{max_value}",
            False,
            f"missing_column={column}",
        )
        return

    invalid_count = int(
        ((df[column] < min_value) | (df[column] > max_value)).fillna(False).sum()
    )

    passed = invalid_count == 0
    details = "ok" if passed else f"invalid_values={invalid_count}"

    _add_check(
        checks,
        layer,
        table,
        f"{column}_between_{min_value}_and_{max_value}",
        passed,
        details,
    )


def run_basic_quality_checks(config: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta validaciones básica sobre las capas Silver y Gold."""

    silver_path = Path(config["paths"]["silver"])
    gold__path = Path(config["paths"]["gold"])
    quality_path = Path(config["paths"]["quality"])
    quality_path.mkdir(parents=True, exist_ok=True)

    print("Iniciando validaciones básicas de calidad...")

    checks: list[dict[str, Any]] = []

    silver_required_columns = {
        "customers": ["customer_id", "customer_unique_id"],
        "orders": ["order_id", "customer_id", "order_status"],
        "order_items": ["order_id", "product_id", "seller_id", "price"],
        "order_payments": ["order_id", "payment_type", "payment_value"],
        "order_reviews": ["review_id", "order_id", "review_score"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
    }

    gold_required_columns = {
        "dim_customers": ["customer_id", "customer_unique_id"],
        "dim_products": ["product_id"],
        "dim_sellers": ["seller_id"],
        "fact_orders": ["order_id", "customer_id"],
        "fact_order_items": ["order_id", "product_id", "seller_id", "price"],
        "fact_payments": ["order_id", "payment_type", "payment_value"],
        "fact_reviews": ["review_id", "order_id", "review_score"],
        "fact_delivery": ["order_id", "delivery_days", "is_late_delivery"],
        "agg_sales_by_month": ["year_month", "total_orders", "total_sales"],
        "agg_sales_by_category": ["product_category_name_english", "total_sales"],
        "agg_delivery_performance": ["year_month", "late_delivery_rate"],
        "agg_seller_performance": ["seller_id", "total_sales"],
        "agg_customer_satisfaction": ["year_month", "avg_review_score"],
    }

    for table_name, required_columns in silver_required_columns.items():
        df = _read_table(silver_path, table_name)

        _check_not_empty(checks, "silver", table_name, df)
        _check_required_columns(checks, "silver", table_name, df, required_columns)

    for table_name, required_columns in gold_required_columns.items():
        df = _read_table(gold__path, table_name)

        _check_not_empty(checks, "gold", table_name, df)
        _check_required_columns(checks, "gold", table_name, df, required_columns)

    fact_orders = _read_table(gold__path, "fact_orders")
    fact_order_items = _read_table(gold__path, "fact_order_items")
    fact_payments = _read_table(gold__path, "fact_payments")
    fact_reviews = _read_table(gold__path, "fact_reviews")

    _check_no_nulls(checks, "gold", "fact_orders", fact_orders, ["order_id"])
    _check_no_nulls(
        checks,
        "gold",
        "fact_order_items",
        fact_order_items,
        ["order_id", "product_id", "seller_id"],
    )
    _check_no_nulls(checks, "gold", "fact_payments", fact_payments, ["order_id"])
    _check_no_nulls(
        checks,
        "gold",
        "fact_reviews",
        fact_reviews,
        ["review_id", "order_id"],
    )

    _check_non_negative_values(
        checks,
        "gold",
        "fact_order_items",
        fact_order_items,
        ["price", "freight_value", "total_item_value"],
    )

    _check_non_negative_values(
        checks,
        "gold",
        "fact_payments",
        fact_payments,
        ["payment_value"],
    )

    _check_values_between(
        checks,
        "gold",
        "fact_reviews",
        fact_reviews,
        "review_score",
        1,
        5,
    )

    failed_checks = [check for check in checks if not check["passed"]]

    quality_report = {
        "execution_time_utc": datetime.now(UTC).isoformat(),
        "total_checks": len(checks),
        "passed_checks": len(checks) - len(failed_checks),
        "failed_checks": len(failed_checks),
        "success": len(failed_checks) == 0,
        "checks": checks,
    }

    report_path = quality_path / "basic_quality_report.json"

    with report_path.open(mode="w", encoding="utf-8") as file:
        json.dump(quality_report, file, ensure_ascii=False, indent=2)

    print(
        "Validaciones basicas finalizadas | "
        f"correctas: {quality_report['passed_checks']} | "
        f"fallidas: {quality_report['failed_checks']}"
    )

    if failed_checks:
        raise ValueError(
            "Fallaron validaciones basicas de calidad. "
            f"Revisa el reporte: {report_path}"
        )

    return quality_report
