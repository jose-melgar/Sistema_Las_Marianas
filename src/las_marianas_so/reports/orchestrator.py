"""
Orquestador de Reportes.
Carga, instancia y ejecuta los generadores de reportes.
"""
import importlib
from pathlib import Path
from typing import Dict, Any, Type

# Ahora la importación funcionará porque el archivo existe
from .config_loader import load_report_config
from .generators.base import BaseReportGenerator

def _get_generator_class(class_path: str) -> Type[BaseReportGenerator]:
    """Importa dinámicamente una clase por su ruta."""
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

class ReportOrchestrator:
    def __init__(self, loader_data: Dict[str, Any], base_output_path: Path):
        self.loader_data = loader_data
        self.base_output_path = base_output_path
        self.report_registry = load_report_config()

    def list_available_reports(self) -> Dict[str, Dict]:
        """Devuelve el diccionario de reportes disponibles."""
        return self.report_registry

    def run_report(self, report_id: str, params: Dict[str, Any]) -> bool:
        """Ejecuta un reporte específico por su ID."""
        report_config = self.report_registry.get(report_id)
        if not report_config:
            print(f"Error: Reporte con ID '{report_id}' no encontrado en la configuración.")
            return False
        
        try:
            GeneratorClass = _get_generator_class(report_config['generator_class'])
            generator_instance = GeneratorClass(self.loader_data, self.base_output_path)
            
            # Pasamos tanto el ID como la configuración completa al generador
            return generator_instance.generate(report_id=report_id, report_config=report_config, **params)
            
        except (ImportError, AttributeError) as e:
            print(f"Error al cargar la clase del generador para '{report_id}': {e}")
            return False
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la generación del reporte '{report_id}': {e}")
            return False