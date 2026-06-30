import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def generate_execution_report(
    config: dict[str, Any],
    bronze_summary: dict[str, int],
    silver_summary: dict[str, int],
    gold_summary: dict[str, int],
    basic_quality_report: dict[str, Any],
    gx_quality_report: dict[str, Any],
) -> dict[str, Any]:
    """Genera un reporte general de ejecución del pipeline."""

    reports_path = Path(config["paths"]["reports"])
    reports_path.mkdir(parents=True, exist_ok=True)

    execution_report = {
        "project": config["project"]["name"],
        "version": config["project"]["version"],
        "execution_time_utc": datetime.now(UTC).isoformat(),
        "pipeline_status": "success",
        "layers": {
            "bronze": {
                "tables_processed": len(bronze_summary),
                "records_by_table": bronze_summary,
            },
            "silver": {
                "tables_processed": len(silver_summary),
                "records_by_table": silver_summary,
            },
            "gold": {
                "tables_processed": len(gold_summary),
                "records_by_table": gold_summary,
            },
        },
        "quality": {
            "basic_checks": {
                "total_checks": basic_quality_report["total_checks"],
                "passed_checks": basic_quality_report["passed_checks"],
                "failed_checks": basic_quality_report["failed_checks"],
                "success": basic_quality_report["success"],
            },
            "great_expectations": {
                "total_validations": gx_quality_report["total_validations"],
                "passed_validations": gx_quality_report["passed_validations"],
                "failed_validations": gx_quality_report["failed_validations"],
                "success": gx_quality_report["success"],
            },
        },
    }

    reports_path = reports_path / "execution_report.json"

    with reports_path.open(mode="w", encoding="utf-8") as file:
        json.dump(execution_report, file, ensure_ascii=False, indent=2)

    print(f"Reporte de ejecucion generado: {reports_path}")

    return execution_report
