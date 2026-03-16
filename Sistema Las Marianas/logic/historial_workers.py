"""
logic/historial_workers.py

Total trabajadores activos (según Historial_Trabajadores):
Replica la lógica de:
- obra = obra_sel
- fecha_ingreso <= (año/mes seleccionados)
- fecha_salida está vacía OR fecha_salida > (año/mes seleccionados)
"""

from __future__ import annotations

import pandas as pd

from logic.accidents import mes_texto_a_num


def total_trabajadores_activos(df_historial: pd.DataFrame, obra_sel: str, anio_sel: int, mes_texto: str) -> int:
    obra_sel = str(obra_sel).strip()
    mes_num = mes_texto_a_num(mes_texto)
    anio_sel = int(anio_sel)

    fi = pd.to_datetime(df_historial["fecha_ingreso"], errors="coerce")
    fs = pd.to_datetime(df_historial["fecha_salida"], errors="coerce")

    mask_obra = df_historial["obra"].astype(str).str.strip() == obra_sel

    # Ingreso <= periodo seleccionado
    ingreso_antes = (fi.dt.year < anio_sel) | ((fi.dt.year == anio_sel) & (fi.dt.month <= mes_num))
    ingreso_antes = ingreso_antes.fillna(False)

    # Salida vacía o posterior al periodo seleccionado
    salida_vacia = fs.isna()
    salida_despues = (fs.dt.year > anio_sel) | ((fs.dt.year == anio_sel) & (fs.dt.month > mes_num))
    salida_despues = salida_despues.fillna(False)

    mask_activo = salida_vacia | salida_despues

    return int((mask_obra & ingreso_antes & mask_activo).sum())