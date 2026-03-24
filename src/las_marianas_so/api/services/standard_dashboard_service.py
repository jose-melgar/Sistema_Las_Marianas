import pandas as pd
from las_marianas_so.reports.standard_report import domain

def _series_to_chart(s: pd.Series):
    if s is None or len(s) == 0:
        return {"labels": [], "values": []}
    return {
        "labels": [str(i) for i in s.index.tolist()],
        "values": [int(v) for v in s.fillna(0).astype(int).tolist()]
    }

def build_dashboard(data: dict, obra: str, year: int, month: int):
    df_activos = domain.get_active_workers(data, obra, year, month)
    stats = domain.calculate_all_statistics(df_activos, data["trabajadores"], year, month)

    # KPIs básicos
    total_trabajadores = int(len(data["trabajadores"])) if "trabajadores" in data else 0
    total_activos = int(len(df_activos))
    c1 = stats.get("apartado_c1", pd.Series(dtype=int))
    con_emo = int(c1.get("Con EMO Registrado", 0))
    sin_emo = int(c1.get("Sin EMO Registrado", 0))

    c2 = stats.get("apartado_c2", pd.Series(dtype=int))
    entregados_mes = int(c2.get("EMOs entregados en el mes", 0))
    pendientes = int(c2.get("Total de EMOs pendientes", 0))

    return {
        "meta": {"report_type": "standard", "obra": obra, "year": year, "month": month},
        "kpis": {
            "total_trabajadores": total_trabajadores,
            "trabajadores_activos": total_activos,
            "con_emo": con_emo,
            "sin_emo": sin_emo,
            "emos_entregados_mes": entregados_mes,
            "emos_pendientes": pendientes,
        },
        "summaries": {
            "a": domain.generate_text_A(stats["apartado_a"]),
            "b": domain.generate_text_B(stats["apartado_b"]),
            "c1": domain.generate_text_C1(stats["apartado_c1"]),
            "c2": domain.generate_text_C2(stats["apartado_c2"]),
            "d": domain.generate_text_D(stats["apartado_d"]),
            "e": domain.generate_text_E(stats["apartado_e"]),
            "f": domain.generate_text_F(stats["apartado_f"]),
        },
        "charts": {
            "a": _series_to_chart(stats["apartado_a"]["Cantidad"] if "Cantidad" in stats["apartado_a"] else pd.Series(dtype=int)),
            "b": _series_to_chart(stats["apartado_b"]),
            "c1": _series_to_chart(stats["apartado_c1"]),
            "c2": _series_to_chart(stats["apartado_c2"]),
            "e": _series_to_chart(stats["apartado_e"] if isinstance(stats["apartado_e"], pd.Series) else pd.Series(dtype=int)),
        }
    }