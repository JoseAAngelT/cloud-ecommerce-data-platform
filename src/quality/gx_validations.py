from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import Any
from uuid import uuid4

import great_expectations as gx
import pandas as pd


def _read_gold_table(gold_path: Path, table_name: str) -> pd.DataFrame:
    """Lee una tabla Gold en formato Parquet."""

    file_path = gold_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro la tabla Gold: {file_path}")

    return pd.read_parquet(file_path)


def _create_batch(context: Any, df: pd.DataFrame, table_name: str) -> Any:
    """Crea un batch de Great Expectations desde un DataFrame de pandas."""

    unique_id = uuid4().hex[:8]

    data_source = context.data_sources.add_pandas(
        name=f"pandas_{table_name}_asset_{unique_id}"
    )
    data_asset = data_source.add_dataframe_asset(name=f"{table_name}_asset_{unique_id}")
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        name=f"{table_name}_batch_{unique_id}"
    )

    return batch_definition.get_batch(batch_parameters={"dataframe": df})


def _run_expectation(batch: Any, table_name: str, expectation: Any) -> dict[str, Any]:
    """Ejecuta una expectativa de Great Expectations y resume el resultado."""

    try:
        validation_result = batch.validate(expectation)
        result_details = getattr(validation_result, "result", {})

        return {
            "table": table_name,
            "expectation": expectation.__class__.__name__,
            "success": bool(getattr(validation_result, "success", False)),
            "unexpected_count": result_details.get("unexpected_count"),
            "unexpected_percent": result_details.get("unexpected_percet"),
        }

    except Exception as error:
        return {
            "table": table_name,
            "expectation": expectation.__class__.__name__,
            "success": False,
            "error": str(error),
        }


def _gx_expectation(expectation_name: str, **kwargs: Any) -> Any:
    """Crea una expectativa de Great Expectations evitando errores de Pylance."""

    expectation_module = import_module("great_expectations.expectations")
    expectation_class = getattr(expectation_module, expectation_name)
    return expectation_class(**kwargs)


def run_gx_validations(config: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta validaciones de Great Expectations sobre las tablas Gold."""

    gold_path = Path(config["paths"]["gold"])
    quality_path = Path(config["paths"]["quality"])
    quality_path.mkdir(parents=True, exist_ok=True)

    print("Iniciando validaciones con Great Expectations...")

    context = gx.get_context()

    expectations_by_table = {
        "fact_orders": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="order_id"),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="customer_id"),
            _gx_expectation(
                "ExpectColumnValuesToBeInSet",
                column="order_status",
                value_set=[
                    "approved",
                    "canceled",
                    "created",
                    "delivered",
                    "invoiced",
                    "processing",
                    "shipped",
                    "unavailable",
                ],
            ),
        ],
        "fact_order_items": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="order_id"),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="product_id"),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="seller_id"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="price",
                min_value=0,
            ),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="freight_value",
                min_value=0,
            ),
        ],
        "fact_payments": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="order_id"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="payment_value",
                min_value=0,
            ),
            _gx_expectation(
                "ExpectColumnValuesToBeInSet",
                column="payment_type",
                value_set=[
                    "boleto",
                    "credit_card",
                    "debit_card",
                    "not_defined",
                    "voucher",
                ],
            ),
        ],
        "fact_reviews": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="review_id"),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="order_id"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="review_score",
                min_value=1,
                max_value=5,
            ),
        ],
        "agg_sales_by_month": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="year_month"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="total_sales",
                min_value=0,
            ),
        ],
        "agg_delivery_performance": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="year_month"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="late_delivery_rate",
                min_value=0,
                max_value=1,
            ),
        ],
        "agg_customer_satisfaction": [
            _gx_expectation("ExpectTableRowCountToBeBetween", min_value=1),
            _gx_expectation("ExpectColumnValuesToNotBeNull", column="year_month"),
            _gx_expectation(
                "ExpectColumnValuesToBeBetween",
                column="avg_review_score",
                min_value=1,
                max_value=5,
            ),
        ],
    }

    validation_results = []

    for table_name, expectations in expectations_by_table.items():
        df = _read_gold_table(gold_path, table_name)
        batch = _create_batch(context, df, table_name)

        for expectation in expectations:
            result = _run_expectation(batch, table_name, expectation)
            validation_results.append(result)

    failed_validations = [
        result for result in validation_results if not result["success"]
    ]

    gx_report = {
        "execution_time_utc": datetime.now(UTC).isoformat(),
        "total_validations": len(validation_results),
        "passed_validations": len(validation_results) - len(failed_validations),
        "failed_validations": len(failed_validations),
        "success": len(failed_validations) == 0,
        "validations": validation_results,
    }

    report_path = quality_path / "gx_validation_results.json"
    pd.Series(gx_report).to_json(
        report_path,
        force_ascii=False,
        indent=2,
    )

    print(
        "Validaciones GX finalizadas | "
        f"correctas: {gx_report['passed_validations']} | "
        f"fallidas: {gx_report['failed_validations']}"
    )

    if failed_validations:
        raise ValueError(
            "Fallaron validaciones de Great Expectations. "
            f"Revisa el reporte: {report_path}"
        )

    return gx_report
