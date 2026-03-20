"""
Adaptador que conecta el ReporteEstandarService con el sistema de
orquestación de reportes del proyecto.
"""
from pathlib import Path
from dataclasses import dataclass

from ..base import BaseReportGenerator
from .service import ReporteEstandarService

@dataclass(frozen=True)
class ParametrosReporte:
    """Parámetros de entrada para el servicio de generación."""
    obra: str
    year: int
    month: int
    data: dict
    template_path: Path
    output_dir: Path
    temp_dir: Path

class ReporteEstandarGenerator(BaseReportGenerator):
    """
    Este 'puente' es llamado por el orquestador y se encarga de
    instanciar y ejecutar el servicio de reporte específico.
    """
    def generate(self, report_id: str, report_config: dict, **kwargs: any) -> bool:
        """
        Traduce la llamada del orquestador al formato que el servicio espera.
        """
        # Ya no necesita cargar la config, la recibe como parámetro.
        if not report_config:
            print("Error: La configuración del reporte está vacía.")
            return False

        output_dir = self.base_output_path / "informes"
        temp_dir = self.base_output_path / "charts" / report_id

        params = ParametrosReporte(
            obra=kwargs['obra'],
            year=kwargs['year'],
            month=kwargs['month'],
            data=self.data,
            template_path=Path(report_config['template_path']),
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        try:
            print(f"\nIniciando generación del Reporte Estándar para '{params.obra}'...")
            service = ReporteEstandarService(params)
            service.generar()
            print("Generación completada exitosamente.")
            return True
        except Exception as e:
            print(f"\nOcurrió un error durante la generación del reporte: {e}")
            import traceback
            traceback.print_exc() # Para obtener un rastreo detallado si algo más falla
            return False