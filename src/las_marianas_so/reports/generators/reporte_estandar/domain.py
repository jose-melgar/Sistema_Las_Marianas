"""
Lógica de negocio para el Informe EMO Estándar.
Adaptación de `domain.py` del repositorio 'temporal' para funcionar con el loader centralizado.
"""
import calendar
import re
from datetime import date
import pandas as pd

# --- Funciones de utilidad ---

def last_day_of_month(year: int, month: int) -> date:
    """Obtiene el último día de un mes y año dados."""
    return date(year, month, calendar.monthrange(year, month)[1])

def _normalize_sexo_label(sexo_raw: str) -> str:
    """Normaliza etiquetas de sexo a 'Masculino' o 'Femenino'."""
    s = (sexo_raw or "").strip().casefold()
    if s in {"m", "masculino", "h", "hombre"}: return "Masculino"
    if s in {"f", "femenino", "mujer"}: return "Femenino"
    return "Otro"

# --- Funciones de filtrado y preparación de datos ---

def get_obras_from_trabajadores(trabajadores: pd.DataFrame) -> list[str]:
    """Obtiene la lista única de obras/plantas desde la hoja de trabajadores."""
    obras = trabajadores['obra'].dropna().astype(str).str.strip()
    return sorted(obras[obras != ""].unique().tolist())

def get_active_dnis(historial: pd.DataFrame, obra_planta: str, year: int, month: int) -> set[str]:
    """Obtiene los DNIs de los trabajadores activos en una obra y período."""
    cutoff = pd.Timestamp(last_day_of_month(year, month))
    df = historial.copy()
    mask_obra = df["obra"].str.casefold() == obra_planta.strip().casefold()
    mask_activo = df["fecha_salida"].isnull() | (df["fecha_salida"] > cutoff)
    active_dnis = df.loc[mask_obra & mask_activo, "dni"]
    return set(active_dnis[active_dnis != ""].unique())

def filter_trabajadores_activos(trabajadores: pd.DataFrame, active_dnis: set[str]) -> pd.DataFrame:
    """Filtra el DataFrame de trabajadores para obtener solo los activos."""
    return trabajadores[trabajadores['dni'].isin(active_dnis)].copy()

# --- Funciones de cálculo para cada apartado del informe ---

# A) Epidemiología
def calc_epidemiologia_laboral(df_trab: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    df = df_trab.copy()
    df['sexo_norm'] = df['sexo'].apply(_normalize_sexo_label)
    total = len(df)
    resumen = df.groupby("sexo_norm").agg(Cantidad=("sexo_norm", "size"), EdadProm=("edad", "mean")).reset_index()
    resumen["%"] = (resumen["Cantidad"] / total * 100).round(1) if total > 0 else 0
    texto = "Distribución: " + ", ".join([f"{r.sexo_norm}: {r.Cantidad} ({r['%']:.1f}%)" for _, r in resumen.iterrows()])
    return resumen, texto

# B) Grupo Etario
def calc_edad_rangos(df_trab: pd.DataFrame) -> tuple[pd.Series, str]:
    bins = [-1, 19, 29, 39, 49, 59, float("inf")]
    labels = ["<20", "20-29", "30-39", "40-49", "50-59", ">=60"]
    counts = pd.cut(df_trab['edad'], bins=bins, labels=labels).value_counts().reindex(labels).fillna(0).astype(int)
    total = int(counts.sum())
    texto = "Distribución por rangos: " + (", ".join([f"{k}: {v} ({v/total*100:.1f}%)" for k, v in counts.items()]) if total > 0 else "Sin datos")
    return counts, texto

# C) Estatus EMOs
def calc_estatus_emos(registro_emo: pd.DataFrame, active_dnis: set[str]) -> tuple[dict, str]:
    df = registro_emo[registro_emo['dni'].isin(active_dnis)].copy()
    df = df.dropna(subset=['fecha_emo']).sort_values('fecha_emo')
    last_emos = df.groupby('dni').tail(1)
    total = len(last_emos)
    recibidos = int(last_emos['fecha_entrega'].notna().sum())
    pendientes = total - recibidos
    stats = {"total": total, "recibidos": recibidos, "pendientes": pendientes}
    texto = f"Estatus EMO: Recibieron: {recibidos}, Pendientes: {pendientes}"
    return stats, texto

# D) Perfiles de EMO
def calc_perfiles(df_trab: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, str]:
    df = df_trab.copy()
    df['sexo_norm'] = df['sexo'].apply(_normalize_sexo_label)
    def map_perfil(x: str) -> str | None:
        xcf = (x or "").casefold()
        if "oficina" in xcf: return "Oficina"
        if "técnico" in xcf or "tecnico" in xcf: return "Operativo"
        return None
    df['perfil_norm'] = df['perfil'].apply(map_perfil)
    df = df.dropna(subset=['perfil_norm'])
    
    tabla = pd.crosstab(df["perfil_norm"], df["sexo_norm"])
    totals = df["perfil_norm"].value_counts()
    texto = "Distribución por perfiles: " + ", ".join([f"{k}: {v}" for k, v in totals.items()])
    return tabla, totals, texto

# E) Vigencia de EMO
def calc_vigencia(df_trab: pd.DataFrame) -> tuple[pd.Series, str]:
    def classify(v: str) -> str:
        v = (v or "").casefold()
        if "vig" in v: return "Vigente"
        if "venc" in v: return "Vencido"
        return "Sin EMO"
    counts = df_trab['vigencia'].apply(classify).value_counts().reindex(["Vigente", "Vencido", "Sin EMO"]).fillna(0).astype(int)
    texto = "Vigencia de EMO: " + ", ".join([f"{k}: {v}" for k, v in counts.items()])
    return counts, texto

# F) Aptitud Médica
def calc_aptitud(df_trab: pd.DataFrame) -> dict:
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
    counts_total = df['aptitud_norm'].value_counts().reindex(order).fillna(0)
    counts_f = df[df['sexo_norm'] == "Femenino"]['aptitud_norm'].value_counts().reindex(order).fillna(0)
    counts_m = df[df['sexo_norm'] == "Masculino"]['aptitud_norm'].value_counts().reindex(order).fillna(0)
    
    return {"counts_total": counts_total, "counts_f": counts_f, "counts_m": counts_m}