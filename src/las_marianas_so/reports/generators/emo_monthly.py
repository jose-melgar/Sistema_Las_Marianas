"""
Generador del Informe Mensual de EMOs (Apartados A-F).

Implementa la lógica para generar el informe en formato .docx y los
gráficos asociados, consumiendo los datos del loader y la lógica de dominio.
"""
import pandas as pd
from pathlib import Path

from las_marianas_so.domain import emo_domain
from las_marianas_so.reports.generators.base import BaseReportGenerator
from las_marianas_so.reports import chart_utils, word_writer

class EMOMonthlyReportGenerator(BaseReportGenerator):
    """
    Generador para el informe EMO mensual. Produce un .docx y gráficos .png.
    """

    def generate(self, obra: str, year: int, month: int) -> bool:
        """
        Genera el informe EMO para una obra, año y mes específicos.
        """
        print(f"\nGenerando Informe EMO para '{obra}' - {month}/{year}...")
        
        # --- 1. Definir rutas de salida ---
        report_filename_slug = f"informe_emo_{obra.lower().replace(' ', '_')}_{year}_{month:02d}"
        docx_output_path = self.base_output_path / "informes"
        charts_output_path = self.base_output_path / "charts" / report_filename_slug
        
        # --- 2. Preparar datos ---
        df_trabajadores = self.data['trabajadores']
        df_historial = self.data['historial_trabajadores']
        
        df_active = emo_domain.get_active_workers(df_trabajadores, df_historial, obra, year, month)
        if df_active.empty:
            print(f"ADVERTENCIA: No se encontraron trabajadores activos para '{obra}' en {month}/{year}. No se generará el informe.")
            return False

        # --- 3. Generar Gráficos ---
        print(" -> Generando gráficos...")
        # A) Epidemiología
        stats_sexo = emo_domain.calculate_stats_A_epidemiology(df_active)
        chart_utils.create_donut_chart(stats_sexo, "A. Distribución por Sexo", charts_output_path, "A_distribucion_sexo.png")

        # B) Grupo Etario
        stats_edad = emo_domain.calculate_stats_B_age_group(df_active)
        chart_utils.create_barh_chart(stats_edad, "B. Distribución por Grupo Etario", "Nº de Trabajadores", charts_output_path, "B_grupo_etario.png")
        
        # (Aquí irían las llamadas para generar los demás gráficos C, E, F...)

        # --- 4. Generar Documento Word ---
        print(" -> Generando documento Word...")
        doc = word_writer.create_styled_document()
        word_writer.add_main_title(doc, f"INFORME MENSUAL DE VIGILANCIA MÉDICO OCUPACIONAL\n{obra.upper()} - {month:02d}/{year}")

        # Sección A
        word_writer.add_section_title(doc, "A. Análisis Epidemiológico por Sexo")
        doc.add_picture(str(charts_output_path / "A_distribucion_sexo.png"), width=pd. Inches(5))
        
        # Sección B
        word_writer.add_section_title(doc, "B. Análisis por Grupo Etario")
        doc.add_picture(str(charts_output_path / "B_grupo_etario.png"), width=pd. Inches(5))
        
        # (Aquí se agregarían las demás secciones al documento)

        # --- 5. Guardar el documento ---
        word_writer.save_document(doc, docx_output_path, f"{report_filename_slug}.docx")

        print("\nInforme EMO generado exitosamente.")
        return True