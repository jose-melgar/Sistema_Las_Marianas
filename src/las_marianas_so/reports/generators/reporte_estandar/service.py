"""
Servicio de Orquestación para la generación del Reporte Estándar EMO.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pandas as pd

# Imports actualizados para reflejar la nueva ubicación
from . import domain
from . import charts
from . import word_writer

@dataclass(frozen=True)
class ParametrosReporte:
    """Parámetros de entrada para la generación del reporte."""
    obra: str
    year: int
    month: int
    data: dict[str, pd.DataFrame] # Los DataFrames ya cargados por el sistema
    template_path: Path
    output_dir: Path
    temp_dir: Path

class ReporteEstandarService:
    """
    Orquesta la generación del reporte estándar EMO, llenando una plantilla
    Word con datos, tablas y gráficos.
    """
    def __init__(self, params: ParametrosReporte):
        self.p = params
        self.trabajadores = params.data['trabajadores']
        self.historial = params.data['historial_trabajadores']
        self.registro_emo = params.data['registro_emo']
        
        # Crear directorios si no existen
        self.p.output_dir.mkdir(parents=True, exist_ok=True)
        self.p.temp_dir.mkdir(parents=True, exist_ok=True)

    def _anchor(self, doc, title_text: str):
        """Encuentra el párrafo ancla en el documento."""
        p = word_writer.find_paragraph_smart(doc, title_text)
        if p is None:
            raise ValueError(f"No se encontró el título ancla: '{title_text}' en la plantilla.")
        return p

    def generar(self) -> Path:
        """
        Método principal que ejecuta la generación completa del informe.
        """
        active_dnis = domain.get_active_dnis(self.historial, self.p.obra, self.p.year, self.p.month)
        df_activos = domain.filter_trabajadores_activos(self.trabajadores, active_dnis)

        safe_obra = self.p.obra.replace("/", "-")
        month_name = domain.month_name_es(self.p.month)
        report_name = f"INFORME_ESTANDAR_{safe_obra}_{month_name}_{self.p.year}.docx"
        report_path = self.p.output_dir / report_name

        if not self.p.template_path.exists():
            raise FileNotFoundError(f"No se encontró la plantilla Word en: {self.p.template_path}")

        doc = word_writer.open_template(self.p.template_path)

        # A) Epidemiología laboral
        self._inject_epidemiologia(doc, df_activos)

        # B) Grupo Etario
        self._inject_grupo_etario(doc, df_activos)

        # C) Estatus EMO
        self._inject_estatus_emo(doc, active_dnis)

        # D) Perfiles
        self._inject_perfiles_emo(doc, df_activos)
        
        # E) Vigencia
        self._inject_vigencia_emo(doc, df_activos)

        # F) Aptitud
        self._inject_aptitud_emo(doc, df_activos)

        word_writer.save(doc, report_path)
        return report_path

    # --- Métodos privados para cada sección del reporte ---

    def _inject_epidemiologia(self, doc, df_activos):
        resumen_a = domain.calc_epidemiologia_laboral(df_activos)
        img_a_path = self.p.temp_dir / "A_epidemiologia_3d.png"
        charts.donut_3d_stairs(
            labels=resumen_a["Sexo"].astype(str).tolist(),
            values=resumen_a["Cantidad"].tolist(),
            title="Gráfico N°01: Sexo",
            out_path=img_a_path,
        )
        pic_a = word_writer.insert_picture_after_text(doc, "Epidemiología laboral", img_a_path, width_inches=5.8)
        word_writer.insert_paragraph_after_paragraph(pic_a, domain.calc_epidemiologia_text(resumen_a))

    def _inject_grupo_etario(self, doc, df_activos):
        counts_b = domain.calc_edad_rangos(df_activos)
        img_b_path = self.p.temp_dir / "B_edades_barras.png"
        charts.barh_chart(
            categories=list(counts_b.index),
            values=counts_b.values,
            title="Gráfico N°02: Cantidad de trabajadores según edad",
            xlabel="Cantidad",
            out_path=img_b_path,
        )
        pic_b = word_writer.insert_picture_after_text(doc, "Gráfico N°02", img_b_path, width_inches=6.8)
        word_writer.insert_paragraph_after_paragraph(pic_b, domain.calc_edad_text(counts_b))

    def _inject_estatus_emo(self, doc, active_dnis):
        stats_c = domain.calc_estatus_emos(self.registro_emo, active_dnis)
        img_c_path = self.p.temp_dir / "C_estatus_3d.png"
        charts.donut_3d_stairs(
            labels=["Recibieron", "Pendientes"],
            values=[stats_c["recibidos"], stats_c["pendientes"]],
            title="Estatus de EMOS",
            out_path=img_c_path,
        )
        pic_c = word_writer.insert_picture_after_text(doc, "Estados de EMOS", img_c_path, width_inches=5.8)
        word_writer.insert_paragraph_after_paragraph(pic_c, domain.calc_estatus_emos_text(stats_c))
        
    def _inject_perfiles_emo(self, doc, df_activos):
        stats_d = domain.calc_perfiles(df_activos)
        img_d_path = self.p.temp_dir / "D_perfiles_anillo.png"
        charts.donut_chart(
            labels=list(stats_d["totals"].index),
            values=stats_d["totals"].values,
            title="Perfiles de EMO",
            out_path=img_d_path,
        )
        pic_d = word_writer.insert_picture_after_text(doc, "Perfiles de EMO", img_d_path, width_inches=6.4)
        word_writer.insert_paragraph_after_paragraph(pic_d, domain.calc_perfiles_text(stats_d))

    def _inject_vigencia_emo(self, doc, df_activos):
        counts_e = domain.calc_vigencia(df_activos)
        img_e_path = self.p.temp_dir / "E_vigencia_barras.png"
        charts.barh_chart(
            categories=list(counts_e.index),
            values=counts_e.values,
            title="Gráfico N°03: Vigencia EMOS",
            xlabel="Cantidad",
            out_path=img_e_path,
        )
        pic_e = word_writer.insert_picture_after_text(doc, "Gráfico N°03", img_e_path, width_inches=6.8)
        word_writer.insert_paragraph_after_paragraph(pic_e, domain.calc_vigencia_text(counts_e))

    def _inject_aptitud_emo(self, doc, df_activos):
        stats_f = domain.calc_aptitud(df_activos)
        img_f_path = self.p.temp_dir / "F_aptitud_triple.png"
        charts.triple_donut_aptitud(
            counts_f=stats_f["counts_f"],
            counts_total=stats_f["counts_total"],
            counts_m=stats_f["counts_m"],
            out_path=img_f_path,
        )
        pic_f = word_writer.insert_picture_after_text(doc, "Gráfico N°04", img_f_path, width_inches=7.2)
        word_writer.insert_paragraph_after_paragraph(pic_f, stats_f["text"])