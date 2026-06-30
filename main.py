from src.ingest.ingest_bronze import ingest_csv_to_bronze
from src.load.load_gold_to_postgres import load_gold_to_postgres
from src.quality.data_quality_checks import run_basic_quality_checks
from src.quality.gx_validations import run_gx_validations
from src.transform.gold_transformations import run_gold_transformations
from src.transform.silver_transformations import run_silver_transformations
from src.utils.config import load_config
from src.utils.execution_report import generate_execution_report


def main() -> None:
    """Ejecuta el pipeline principal del proyecto."""

    config = load_config()

    print("Ejecutando Cloud E-Commerce Data Platform...")

    bronze_summary = ingest_csv_to_bronze(config)
    silver_summary = run_silver_transformations(config)
    gold_summary = run_gold_transformations(config)

    basic_quality_report = run_basic_quality_checks(config)
    gx_quality_report = run_gx_validations(config)

    generate_execution_report(
        config=config,
        bronze_summary=bronze_summary,
        silver_summary=silver_summary,
        gold_summary=gold_summary,
        basic_quality_report=basic_quality_report,
        gx_quality_report=gx_quality_report,
    )

    load_gold_to_postgres(config)

    print("Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
