"""
logic/accidents.py
Fórmulas replicadas:

- Total de accidentes (por mes/obra, usando buscar obra por DNI en Trabajadores)
- Total de accidentados únicos (por mes/obra)
- Parte del cuerpo más accidentada (Top 15, o "Sin accidentes")
- Objeto que provocó el accidente (ranking por Agente, o "Sin accidentes")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import pandas as pd


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def mes_texto_a_num(mes_texto: str) -> int:
    mes_texto = str(mes_texto).strip()
    if mes_texto not in MESES:
        raise ValueError(f"Mes inválido: '{mes_texto}'. Debe ser uno de: {', '.join(MESES)}")
    return MESES.index(mes_texto) + 1


def _attach_obra(df_accidentes: pd.DataFrame, df_trabajadores: pd.DataFrame) -> pd.DataFrame:
    t = df_trabajadores.dropna(subset=["dni"]).copy()
    t = t.sort_values(by=["dni"]).drop_duplicates(subset=["dni"], keep="first")

    a = df_accidentes.copy()
    # buscarx: accidentes.dni -> trabajadores.dni trae obra
    a = a.merge(t[["dni", "obra"]], on="dni", how="left", validate="m:1")
    return a


def _filter_mes_obra(df: pd.DataFrame, mes_num: int, obra_sel: str) -> pd.DataFrame:
    obra_sel = str(obra_sel).strip()

    # Excel: (SI.ERROR(MES(Fecha),0)=mes_num) * (Fecha<>"") * (obra=obra_sel)
    mask_mes = df["fecha"].dt.month.fillna(0).astype(int) == int(mes_num)
    mask_fecha_no_vacia = df["fecha"].notna()
    mask_obra = df["obra"].astype(str).str.strip() == obra_sel

    return df.loc[mask_mes & mask_fecha_no_vacia & mask_obra].copy()


def total_accidentes(df_accidentes: pd.DataFrame, df_trabajadores: pd.DataFrame, mes_texto: str, obra_sel: str) -> int:
    mes_num = mes_texto_a_num(mes_texto)
    df = _attach_obra(df_accidentes, df_trabajadores)
    f = _filter_mes_obra(df, mes_num, obra_sel)
    return int(len(f))


def total_accidentados_unicos(df_accidentes: pd.DataFrame, df_trabajadores: pd.DataFrame, mes_texto: str, obra_sel: str) -> int:
    mes_num = mes_texto_a_num(mes_texto)
    df = _attach_obra(df_accidentes, df_trabajadores)
    f = _filter_mes_obra(df, mes_num, obra_sel)
    unicos = f["dni"].dropna().astype(str).unique()
    return int(len(unicos))


def ranking_parte_cuerpo_top15(
    df_accidentes: pd.DataFrame,
    df_trabajadores: pd.DataFrame,
    mes_texto: str,
    obra_sel: str,
) -> Union[str, pd.DataFrame]:
    mes_num = mes_texto_a_num(mes_texto)
    df = _attach_obra(df_accidentes, df_trabajadores)
    f = _filter_mes_obra(df, mes_num, obra_sel)

    s = f["parte_cuerpo"].dropna().astype(str).str.strip()
    if s.empty:
        return "Sin accidentes"

    vc = s.value_counts().head(15)
    return vc.rename_axis("ParteCuerpo").reset_index(name="Conteo")


def ranking_agente(
    df_accidentes: pd.DataFrame,
    df_trabajadores: pd.DataFrame,
    mes_texto: str,
    obra_sel: str,
) -> Union[str, pd.DataFrame]:
    mes_num = mes_texto_a_num(mes_texto)
    df = _attach_obra(df_accidentes, df_trabajadores)
    f = _filter_mes_obra(df, mes_num, obra_sel)

    s = f["agente"].dropna().astype(str).str.strip()
    if s.empty:
        return "Sin accidentes"

    vc = s.value_counts()
    return vc.rename_axis("Agente").reset_index(name="Conteo")