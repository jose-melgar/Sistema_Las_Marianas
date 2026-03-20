"""
Servicio de Orquestación para la generación del Reporte Estándar EMO.
Versión completa y fiel adaptada del repositorio 'temporal'.
"""
from pathlib import Path
from docx import Document

# Imports actualizados para reflejar la nueva ubicación
from . import domain
from . import charts
from . import word_writer
from .generator import ParametrosReporte # Importa la clase de parámetros

class ReporteEstandarService:
    def __init__(self, params: ParametrosReporte):
        self.p = params
        self.trabajadores = params.data['trabajadores']
        self.historial = params.data['historial_trabajadores']
        self.registro_emo = params.data['registro_emo']
        self.p.output_dir.mkdir(parents=True, exist_ok=True)
        self.p.temp_dir.mkdir(parents=True, exist_ok=True)

    def generar(self) -> Path:
        active_dnis = domain.get_active_dnis(self.historial, self.p.obra, self.p.year, self.p.month)
        df_activos = domain.filter_trabajadores_activos(self.trabajadores, active_dnis)

        safe_obra = self.p.obra.replace("/", "-")
        month_name = domain.month_name_es(self.p.month)
        report_name = f"INFORME_ESTANDAR_{safe_obra}_{month_name}_{self.p.year}.docx"
        report_path = self.p.output_dir / report_name

        doc = word_writer.open_template(self.p.template_path)

        # Inyectar cada sección del reporte
        self._inject_epidemiologia(doc, df_activos)
        self._inject_grupo_etario(doc, df_activos)
        self._inject_estatus_emo(doc, active_dnis)
        self._inject_perfiles_emo(doc, df_activos)
        self._inject_vigencia_emo(doc, df_activos)
        self._inject_aptitud_emo(doc, df_activos)

        word_writer.save(doc, report_path)
        return report_path

    def _get_anchor(self, doc, title_text):
        p = word_writer.find_paragraph_smart(doc, title_text)
        if p is None:
            raise ValueError(f"No se encontró el título ancla: '{title_text}' en la plantilla.")
        return p

    def _inject_epidemiologia(self, doc, df_activos):
        anchor = self._get_anchor(doc, "Epidemiología laboral")
        resumen, texto = domain.calc_epidemiologia_laboral(df_activos)
        img_path = self.p.temp_dir / "A_epidemiologia_3d.png"
        charts.donut_3d_stairs(labels=resumen["sexo_norm"].tolist(), values=resumen["Cantidad"].tolist(), title="Gráfico N°01: Sexo", out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=5.8)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)

    def _inject_grupo_etario(self, doc, df_activos):
        anchor = self._get_anchor(doc, "Gráfico N°02")
        counts, texto = domain.calc_edad_rangos(df_activos)
        img_path = self.p.temp_dir / "B_edades_barras.png"
        charts.barh_chart(categories=list(counts.index), values=counts.values, title="Gráfico N°02: Cantidad de trabajadores según edad", xlabel="Cantidad", out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=6.8)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)

    def _inject_estatus_emo(self, doc, active_dnis):
        anchor = self._get_anchor(doc, "Estados de EMOS")
        stats, texto = domain.calc_estatus_emos(self.registro_emo, active_dnis)
        img_path = self.p.temp_dir / "C_estatus_3d.png"
        charts.donut_3d_stairs(labels=["Recibieron", "Pendientes"], values=[stats["recibidos"], stats["pendientes"]], title="Estatus de EMOS", out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=5.8)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)
        
    def _inject_perfiles_emo(self, doc, df_activos):
        anchor = self._get_anchor(doc, "Perfiles de EMO")
        counts, texto = domain.calc_perfiles(df_activos)
        img_path = self.p.temp_dir / "D_perfiles_anillo.png"
        charts.donut_chart(labels=list(counts.index), values=counts.values, title="Perfiles de EMO", out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=6.4)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)

    def _inject_vigencia_emo(self, doc, df_activos):
        anchor = self._get_anchor(doc, "Gráfico N°03")
        counts, texto = domain.calc_vigencia(df_activos)
        img_path = self.p.temp_dir / "E_vigencia_barras.png"
        charts.barh_chart(categories=list(counts.index), values=counts.values, title="Gráfico N°03: Vigencia EMOS", xlabel="Cantidad", out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=6.8)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)

    def _inject_aptitud_emo(self, doc, df_activos):
        anchor = self._get_anchor(doc, "Gráfico N°04")
        stats, texto = domain.calc_aptitud(df_activos)
        img_path = self.p.temp_dir / "F_aptitud_triple.png"
        charts.triple_donut_aptitud(counts_f=stats["counts_f"], counts_total=stats["counts_total"], counts_m=stats["counts_m"], out_path=img_path)
        p_pic = word_writer.insert_picture_after_paragraph(anchor, img_path, width_inches=7.2)
        word_writer.insert_paragraph_after_paragraph(p_pic, texto)