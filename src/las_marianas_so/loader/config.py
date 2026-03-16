"""
Módulo auxiliar para cargar la configuración YAML del loader.
"""
import yaml
from pathlib import Path

CONFIG_FILE_PATH = Path(__file__).parent.parent.parent.parent / "config/loader.config.yml"

def load_config() -> dict:
    """Carga el archivo de configuración YAML."""
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"El archivo de configuración no se encontró en: {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Carga la configuración una sola vez al iniciar el módulo.
SYSTEM_CONFIG = load_config()