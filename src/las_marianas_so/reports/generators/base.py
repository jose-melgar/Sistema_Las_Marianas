"""
Clase Base para Generadores de Reportes.

Define la interfaz que todos los generadores de reportes deben implementar
para ser compatibles con el orquestador de reportes.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class BaseReportGenerator(ABC):
    """
    Interfaz abstracta para un generador de reportes.
    """

    def __init__(self, loader_data: Dict[str, any], base_output_path: Path):
        """
        Inicializa el generador.

        Args:
            loader_data (Dict[str, any]): Los datos cargados por el ExcelLoader.
            base_output_path (Path): La ruta base para guardar los artefactos (ej: 'outputs/').
        """
        self.data = loader_data
        self.base_output_path = base_output_path

    @abstractmethod
    def generate(self, **kwargs: Any) -> bool:
        """
        Método principal que orquesta la generación del reporte.

        Recibe parámetros específicos del reporte (ej: obra, año, mes)
        y produce los artefactos finales (archivos .docx, .png, etc.).

        Args:
            **kwargs: Argumentos dinámicos requeridos por el reporte.

        Returns:
            bool: True si la generación fue exitosa, False en caso contrario.
        """
        pass