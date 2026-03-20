"""
Módulo dedicado a cargar la configuración de reportes desde el archivo YAML.

Este archivo existe para ser una dependencia neutral y así romper los
ciclos de importación entre el orquestador y los generadores.
"""
import yaml
from pathlib import Path

# Define la ruta al archivo de configuración de forma centralizada
CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "config/reports.config.yml"

def load_report_config() -> dict:
    """
    Carga y devuelve el registro completo de reportes desde el archivo YAML.
    """
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"El archivo de configuración de reportes no se encontró en: {CONFIG_FILE_PATH}")
    
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        if not config or "report_registry" not in config:
            return {}
        return config["report_registry"]