from src.spark.spark_gold import run_spark_gold_sample
from src.utils.config import load_config


def main() -> None:
    """Ejecuta una prueba inicial de Gold con PySpark."""

    config = load_config()
    run_spark_gold_sample(config)


if __name__ == "__main__":
    main()
