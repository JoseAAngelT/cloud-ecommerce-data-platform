from src.ingest.ingest_bronze import ingest_csv_to_bronze
from src.utils.config import load_config


def main() -> None:
    """Ejecuta el pipeline principal del proyecto."""

    config = load_config()

    print("Ejecutando Cloud E-Commerce Data Platform...")
    ingest_csv_to_bronze(config)
    print("Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
