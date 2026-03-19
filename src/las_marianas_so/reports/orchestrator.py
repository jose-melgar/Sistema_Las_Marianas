"""
Orquestador de Reportes.

Este módulo carga la configuración de reportes, los instancia y ejecuta.
Actúa como un 'registry' que permite al CLI descubrir y lanzar
reportes de forma dinámica.
"""
import yaml
import importlib
from pathlib import Path
from typing import Dict, Any, Type

from las_marianas_so.reports.generators.base import BaseReportGenerator

CONFIG_FILE_PATH = Path(__file__).parent.parent.parent.parent / "config/reports.config.yml"

def _load_report_config() -> dict:
    """Carga el archivo de configuración de reportes."""
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"El archivo de configuración de reportes no se encontró en: {CONFIG_FILE_PATH}")
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f).get("report_registry", {})

def _get_generator_class(class_path: str) -> Type[BaseReportGenerator]:
    """Importa dinámicamente la clase del generador de reportes."""
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

class ReportOrchestrator:
    """
    Gestiona la ejecución de reportes definidos en la configuración.
    """
    def __init__(self, loader_data: Dict[str, Any], base_output_path: Path):
        self.loader_data = loader_data
        self.base_output_path = base_output_path
        self.report_registry = _load_report_config()

    def list_available_reports(self) -> Dict[str, Dict]:
        """Devuelve un diccionario de los reportes disponibles."""
        return self.report_registry

    def run_report(self, report_id: str, params: Dict[str, Any]) -> bool:
        """
        Ejecuta un reporte específico por su ID.

        Args:
            report_id (str): La clave del reporte en el registro.
            params (Dict[str, Any]): Un diccionario con los parámetros
                                     necesarios para el generador.

        Returns:
            bool: True si la generación fue exitosa.
        """
        if report_id not in self.report_registry:
            print(f"Error: Reporte con ID '{report_id}' no encontrado.")
            return False

        report_config = self.report_registry[report_id]
        
        try:
            GeneratorClass = _get_generator_class(report_config['generator_class'])
            generator_instance = GeneratorClass(self.loader_data, self.base_output_path)
            
            return generator_instance.generate(report_id=report_id, **params)
            
        except (ImportError, AttributeError) as e:
            print(f"Error al cargar la clase del generador para '{report_id}': {e}")
            return False
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la generación del reporte '{report_id}': {e}")
            return False