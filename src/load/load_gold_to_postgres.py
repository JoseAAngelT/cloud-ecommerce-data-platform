import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def _create_postgres_engine() -> Any:
    """Crea la conexión a PostgreSQL usando variables de entorno."""

    load_dotenv()

    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Faltan variables de entorno: {missing_vars}")

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB"),
    )

    return create_engine(connection_url)


def _read_gold_table(gold_path: Path, table_name: str) -> pd.DataFrame:
    """Lea una tabla Gold desde archivo Parquet."""

    file_path = gold_path / f"{table_name}.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro la tabla Gold: {file_path}")

    return pd.read_parquet(file_path)


def load_gold_to_postgres(config: dict[str, Any]) -> dict[str, int]:
    """Carga las tablas Gold a PostgreSQL."""

    gold_path = Path(config["paths"]["gold"])
    postgres_schema = config["serving"]["postgres_schema"]
    gold_tables = config["serving"]["gold_tables"]

    engine = _create_postgres_engine()

    print("Iniciando carga de Gold a PostgreSQL...")

    load_summary = {}

    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {postgres_schema}"))

        for table_name in gold_tables:
            df = _read_gold_table(gold_path, table_name)

            df.to_sql(
                name=table_name,
                con=connection,
                schema=postgres_schema,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=5000,
            )

            load_summary[table_name] = len(df)

            print(
                f"Tabla cargada en PostgreSQL: "
                f"{postgres_schema}.{table_name} | registros: {len(df):,}"
            )
    print("Carga de Gold a PostgreSQL finalizada correctamente.")

    return load_summary
