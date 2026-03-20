"""
Lógica de negocio para el Informe EMO Estándar.
Versión completa y fiel adaptada del repositorio 'temporal'.
"""
import calendar
import re
from datetime import date
import pandas as pd

def month_name_es(month: int) -> str:
    """Convierte un número de mes a su nombre en español."""
    meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    return meses.get(int(month), f"Mes {month}")

def last_day_of_month(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])

def _normalize_sexo_label(sexo_raw: str) -> str:
    s = (sexo_raw or "").strip().casefold()
    if s in {"m", "masculino", "h", "hombre"}: return "Masculino"
    if s in {"f", "femenino", "mujer"}: return "Femenino"
    return "Otro"

def get_active_dnis(historial: pd.DataFrame, obra_planta: str, year: int, month: int) -> set[str]:
    cutoff = pd.Timestamp(last_day_of_month(year, month))
    df = historial.copy()
    mask_obra = df["obra"].str.casefold() == obra_planta.strip().casefold()
    mask_activo = df["fecha_salida"].isnull() | (pd.to_datetime(df["fecha_salida"]) > cutoff)
    active_dnis = df.loc[mask_obra & mask_activo, "dni"]
    return set(active_dnis.dropna().astype(str).unique())

def filter_trabajadores_activos(trabajadores: pd.DataFrame, active_dnis: set[str]) -> pd.DataFrame:
    return trabajadores[trabajadores['dni'].isin(active_dnis)].copy()

def calc_epidemiologia_laboral(df_trab: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    df = df_trab.copy()
    df['sexo_norm'] = df['sexo'].apply(_normalize_sexo_label)
    total = len(df)
    if total == 0: return pd.DataFrame(columns=["sexo_norm", "Cantidad", "%"]), "Sin datos de epidemiología."
    resumen = df.groupby("sexo_norm").agg(Cantidad=("sexo_norm", "size"), EdadProm=("edad", "mean")).reset_index()
    resumen["%"] = (resumen["Cantidad"] / total * 100).round(1)
    texto = "Distribución por sexo: " + ", ".join([f"{r.sexo_norm}: {r.Cantidad} ({r['%']:.1f}%)" for _, r in resumen.iterrows()])
    return resumen, texto

def calc_edad_rangos(df_trab: pd.DataFrame) -> tuple[pd.Series, str]:
    bins = [-1, 19, 29, 39, 49, 59, float("inf")]
    labels = ["<20", "20-29", "30-39", "40-49", "50-59", ">=60"]
    counts = pd.cut(df_trab['edad'], bins=bins, labels=labels).value_counts().reindex(labels).fillna(0).astype(int)
    total = int(counts.sum())
    texto = "Distribución por rangos de edad: " + (", ".join([f"{k}: {v} ({v/total*100:.1f}%)" for k, v in counts.items()]) if total > 0 else "Sin datos")
    return counts, texto

def calc_estatus_emos(registro_emo: pd.DataFrame, active_dnis: set[str]) -> tuple[dict, str]:
    df = registro_emo[registro_emo['dni'].isin(active_dnis)].copy()
    df = df.dropna(subset=['fecha_emo']).sort_values('fecha_emo')
    last_emos = df.groupby('dni').tail(1)
    total = len(last_emos)
    recibidos = int(last_emos['fecha_entrega'].notna().sum())
    pendientes = total - recibidos
    stats = {"total": total, "recibidos": recibidos, "pendientes": pendientes}
    texto = f"Estatus de entrega EMO: {recibidos} Recibidos, {pendientes} Pendientes de {total} EMOs registrados."
    return stats, texto

def calc_perfiles(df_trab: pd.DataFrame) -> tuple[pd.Series, str]:
    def map_perfil(x: str) -> str | None:
        xcf = (x or "").casefold()
        if "oficina" in xcf: return "Oficina"
        if "técnico" in xcf or "tecnico" in xcf: return "Operativo"
        return None
    counts = df_trab['perfil'].apply(map_perfil).value_counts()
    texto = "Distribución por perfiles: " + ", ".join([f"{k}: {v}" for k, v in counts.items()])
    return counts, texto

def calc_vigencia(df_trab: pd.DataFrame) -> tuple[pd.Series, str]:
    def classify(v: str) -> str:
        v = (v or "").casefold()
        if "vig" in v: return "Vigente"
        if "venc" in v: return "Vencido"
        return "Sin EMO"
    counts = df_trab['vigencia'].apply(classify).value_counts().reindex(["Vigente", "Vencido", "Sin EMO"]).fillna(0).astype(int)
    texto = "Vigencia de EMO: " + ", ".join([f"{k}: {v}" for k, v in counts.items()])
    return counts, texto

def calc_aptitud(df_trab: pd.DataFrame) -> tuple[dict, str]:
    df = df_trab.copy()
    df['sexo_norm'] = df['sexo'].apply(_normalize_sexo_label)
    def map_apt(a: str) -> str:
        a = (a or "OBSERVADO").upper()
        if "NO" in a and "APTO" in a: return "NO APTO"
        if "RESTR" in a: return "CON RESTRICCIONES"
        if "APTO" in a: return "APTO"
        return "OBSERVADO"
    df['aptitud_norm'] = df['aptitud'].apply(map_apt)
    
    order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]
    counts_total = df['aptitud_norm'].value_counts().reindex(order).fillna(0).astype(int)
    counts_f = df[df['sexo_norm'] == "Femenino"]['aptitud_norm'].value_counts().reindex(order).fillna(0).astype(int)
    counts_m = df[df['sexo_norm'] == "Masculino"]['aptitud_norm'].value_counts().reindex(order).fillna(0).astype(int)
    
    stats = {"counts_total": counts_total, "counts_f": counts_f, "counts_m": counts_m}
    
    total = int(counts_total.sum())
    texto_general = "Aptitud general: " + (", ".join([f"{k}: {v} ({v/total*100:.1f}%)" for k, v in counts_total.items()]) if total > 0 else "Sin datos")
    
    return stats, texto_general