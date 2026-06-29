from pathlib import Path

import yaml


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Carga la configuración general del proyecto."""

    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontro el archivo de configuracion: {path}")

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
