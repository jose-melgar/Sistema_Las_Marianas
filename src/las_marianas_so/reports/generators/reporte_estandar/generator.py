"""
Adaptador que conecta el ReporteEstandarService con el sistema de
orquestación de reportes del proyecto.
"""
from pathlib import Path

# Importamos la clase base del sistema
from ..base import BaseReportGenerator 

# Importamos el servicio y los parámetros que necesita
from .service import ReporteEstandarService, ParametrosReporte
from las_marianas_so.reports.orchestrator import _load_report_config

class ReporteEstandarGenerator(BaseReportGenerator):
    """
    Esta clase es el 'puente' o 'adaptador'.
    Hereda de BaseReportGenerator y sabe cómo llamar a ReporteEstandarService.
    """
    def generate(self, report_id: str, **kwargs: any) -> bool:
        """
        Este es el método que el orquestador llama.
        """
        # 1. Cargar la configuración específica de este reporte
        report_config = _load_report_config().get(report_id, {})
        if not report_config:
            print(f"Error: No se encontró la configuración para el reporte ID '{report_id}'.")
            return False

        # 2. Preparar los directorios de salida
        output_dir = self.base_output_path / "informes"
        temp_dir = self.base_output_path / "charts" / report_id

        # 3. Crear el objeto de parámetros que el 'service' espera
        params = ParametrosReporte(
            obra=kwargs['obra'],
            year=kwargs['year'],
            month=kwargs['month'],
            data=self.data,  # Los DataFrames vienen del loader
            template_path=Path(report_config['template_path']),
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        # 4. Instanciar y ejecutar el servicio del reporte estándar
        try:
            print(f"\nIniciando generación del Reporte Estándar para '{params.obra}'...")
            service = ReporteEstandarService(params)
            service.generar()
            print("Generación completada exitosamente.")
            return True
        except Exception as e:
            print(f"\nOcurrió un error durante la generación del reporte: {e}")
            return False