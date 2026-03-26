import pandas as pd
from las_marianas_so.reports.standard_report import domain

def _series_to_chart(s: pd.Series):
    if s is None or len(s) == 0:
        return {"labels": [], "values": []}
    return {
        "labels": [str(i) for i in s.index.tolist()],
        "values": [int(v) for v in s.fillna(0).astype(int).tolist()]
    }

def _empty_chart():
    return {"labels": [], "values": []}

def _get_labels_and_values(s: pd.Series, order=None):
    """
    Convierte una Serie a (labels, values) asegurando el orden y tipado correcto.
    Si la serie es None o está vacía, devuelve listas vacías.
    """
    if s is None or len(s) == 0:
        return [], []
    s = s.copy()
    if order:
        s = s.reindex(order).fillna(0).astype(int)
    return [str(k) for k in s.index], [int(v) for v in s.values]

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

    # APARTADO D (Perfiles de EMO)
    d = stats.get("apartado_d")
    if isinstance(d, dict) and "totals" in d:
        d = d["totals"]
    chart_d = _series_to_chart(d) if isinstance(d, pd.Series) else _empty_chart()

    # APARTADO E (Vigencia)
    e = stats.get("apartado_e")
    chart_e = _series_to_chart(e) if isinstance(e, pd.Series) else _empty_chart()

    # APARTADO F (Aptitud EMO, dona triple)
    f = stats.get("apartado_f")
    order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]
    chart_f = {"labels_f": [], "values_f": [], "labels_total": [], "values_total": [], "labels_m": [], "values_m": []}

    # Ahora 'f' es un diccionario proveído directamente por emo_domain.py
    if isinstance(f, dict):
        chart_f["labels_total"], chart_f["values_total"] = _get_labels_and_values(f.get("counts_total"), order)
        chart_f["labels_f"], chart_f["values_f"] = _get_labels_and_values(f.get("counts_f"), order)
        chart_f["labels_m"], chart_f["values_m"] = _get_labels_and_values(f.get("counts_m"), order)
    elif isinstance(f, pd.Series):
        # Fallback de seguridad por si en algún momento vuelve a ser una Serie
        chart_f["labels_total"], chart_f["values_total"] = _get_labels_and_values(f, order)

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
            "d": chart_d,
            "e": chart_e,
            "f": chart_f,
        }
    }