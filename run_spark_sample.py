from src.spark.spark_silver import run_spark_silver_sample

from src.utils.config import load_config


def main() -> None:
    """Ejecuta una prueba inicial de PySpark."""

    config = load_config()
    run_spark_silver_sample(config)


if __name__ == "__main__":
    main()
