from src.ingest.ingest_bronze import ingest_csv_to_bronze
from src.quality.data_quality_checks import run_basic_quality_checks
from src.quality.gx_validations import run_gx_validations
from src.transform.gold_transformations import run_gold_transformations
from src.transform.silver_transformations import run_silver_transformations
from src.utils.config import load_config


def main() -> None:
    """Ejecuta el pipeline principal del proyecto."""

    config = load_config()

    print("Ejecutando Cloud E-Commerce Data Platform...")

    ingest_csv_to_bronze(config)
    run_silver_transformations(config)
    run_gold_transformations(config)
    run_basic_quality_checks(config)
    run_gx_validations(config)

    print("Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
