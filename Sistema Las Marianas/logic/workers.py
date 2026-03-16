"""
logic/workers.py

Total trabajadores ingresados:
SUMAPRODUCTO((Trabajadores!G=obra) * (MES(FechaIngreso)=mes) * (AÑO(FechaIngreso)=año))
"""

from __future__ import annotations

import pandas as pd

from logic.accidents import mes_texto_a_num


def total_trabajadores_ingresados(df_trabajadores: pd.DataFrame, obra_sel: str, anio_sel: int, mes_texto: str) -> int:
    obra_sel = str(obra_sel).strip()
    mes_num = mes_texto_a_num(mes_texto)
    anio_sel = int(anio_sel)

    fecha = pd.to_datetime(df_trabajadores["fecha_ingreso"], errors="coerce")

    mask_obra = df_trabajadores["obra"].astype(str).str.strip() == obra_sel
    mask_mes = fecha.dt.month.fillna(0).astype(int) == mes_num
    mask_anio = fecha.dt.year.fillna(0).astype(int) == anio_sel

    return int((mask_obra & mask_mes & mask_anio).sum())