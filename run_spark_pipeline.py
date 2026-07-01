from src.spark.spark_gold import run_spark_gold_sample
from src.spark.spark_silver import run_spark_silver_sample
from src.utils.config import load_config


def main() -> None:
    """Ejecuta la versión Spark del pipeline."""

    config = load_config()

    print("Ejecutando pipeline Spark...")
    run_spark_silver_sample(config)
    run_spark_gold_sample(config)
    print("Pipeline Spark finalizado correctamente.")


if __name__ == "__main__":
    main()
