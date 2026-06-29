from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


def ingest_csv_to_bronze(config: dict) -> dict[str, int]:
    """Ingesta archivos CSV desde landing y los guarda en Bronze como Parquet."""

    landing_path = Path(config["paths"]["landing"])
    bronze_path = Path(config["paths"]["bronze"])
    sources = config["bronze"]["sources"]

    if not landing_path.exists():
        raise FileNotFoundError(f"No existe la carpeta landing: {landing_path}")

    bronze_path.mkdir(parents=True, exist_ok=True)

    ingestion_time = datetime.now(UTC).isoformat()
    ingestion_summary = {}

    print("Iniciando ingesta Bronze...")

    for table_name, file_name in sources.items():
        source_file = landing_path / file_name
        output_file = bronze_path / f"{table_name}.parquet"

        if not source_file.exists():
            raise FileNotFoundError(f"No se encontro el archivo fuente: {source_file}")

        df = pd.read_csv(source_file)

        # Metadata técnica de ingesta. No modifica la lógica de negocio.
        df["_ingestion_time_utc"] = ingestion_time
        df["_source_file"] = file_name

        df.to_parquet(output_file, index=False)

        ingestion_summary[table_name] = len(df)

        print(f"Bronze generado: {table_name} | registros: {len(df):,}")

    print("Ingesta Bronze finalizada correctamente.")

    return ingestion_summary
