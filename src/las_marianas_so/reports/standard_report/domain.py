"""
Módulo de Lógica de Negocio para el Reporte Estándar.
Corregido para usar los nombres de columna finales definidos en loader.config.yml.
"""
import pandas as pd
from las_marianas_so.domain import emo_domain

def get_active_workers(data: dict, obra: str, year: int, month: int) -> pd.DataFrame:
    """Filtra y devuelve solo los trabajadores activos para el contexto dado."""
    return emo_domain.get_active_workers(
        df_trabajadores=data['trabajadores'],
        df_historial=data['historial_trabajadores'],
        obra=obra,
        year=year,
        month=month
    )

# --- APARTADO A ---
def calculate_stats_A_epidemiology(df_active: pd.DataFrame) -> pd.DataFrame:
    sexo_map = {'M': 'Masculino', 'F': 'Femenino'}
    df_active['sexo_full'] = df_active['sexo'].map(sexo_map).fillna('Otro')
    resumen = df_active.groupby('sexo_full').agg(
        Cantidad=('sexo_full', 'size'),
        EdadProm=('edad', 'mean')
    ).round({'EdadProm': 1})
    return resumen

def generate_text_A(data: pd.DataFrame) -> str:
    total = data['Cantidad'].sum()
    dist_parts = [f"{sexo}: {int(row['Cantidad'])} ({(row['Cantidad']/total*100):.1f}%)" for sexo, row in data.iterrows()]
    edad_parts = [f"{sexo}: {row['EdadProm']} años" for sexo, row in data.iterrows()]
    return f"Distribución por sexo: {', '.join(dist_parts)}. Edad promedio por sexo: {'; '.join(edad_parts)}."

# --- APARTADO B ---
def calculate_stats_B_age_group(df_active: pd.DataFrame) -> pd.Series:
    bins = [0, 20, 30, 40, 50, 60, 120]
    labels = ['<20', '20-29', '30-39', '40-49', '50-59', '>=60']
    df_active['grupo_etario'] = pd.cut(df_active['edad'], bins=bins, labels=labels, right=False)
    return df_active['grupo_etario'].value_counts().sort_index()

def generate_text_B(data: pd.Series) -> str:
    total = data.sum()
    parts = [f"{idx}: {int(val)} ({(val/total*100):.1f}%)" for idx, val in data.items()]
    return f"Distribución por rangos de edad: {', '.join(parts)}."

# --- APARTADO C: ESTATUS EMO (CORREGIDO CON NOMBRES DE CONFIG.YML) ---

def calculate_stats_C1_cobertura(df_trabajadores: pd.DataFrame) -> pd.Series:
    """Gráfico C_1: Cobertura de EMO (Con EMO vs. Sin EMO)."""
    # CORRECCIÓN: Usamos 'ultimo_emo', que es el nombre renombrado de 'Ultimo EMO'
    con_emo = df_trabajadores[df_trabajadores['ultimo_emo'].notna()].shape[0]
    sin_emo = df_trabajadores[df_trabajadores['ultimo_emo'].isna()].shape[0]
    return pd.Series({'Con EMO Registrado': con_emo, 'Sin EMO Registrado': sin_emo})

def calculate_stats_C2_entrega_mes(df_trabajadores: pd.DataFrame, year: int, month: int) -> pd.Series:
    """Gráfico C_2: Porcentaje Entrega de EMOs."""
    periodo_inicio = pd.to_datetime(f"{year}-{month}-01")
    
    # Usamos el nombre interno 'ultimo_emo'
    con_emo_df = df_trabajadores[df_trabajadores['ultimo_emo'].notna()].copy()
    
    # CORRECCIÓN: Usamos los nombres renombrados por el loader.config.yml
    entregado_col = 'emo_entregado_historial'
    fecha_entrega_col = 'fecha_emo_entregado_historial'
    
    # Las fechas ya fueron convertidas a datetime por el loader
    entregados_mask = (
        (con_emo_df[entregado_col] == 'SI') &
        (con_emo_df[fecha_entrega_col] >= periodo_inicio)
    )
    entregados_count = entregados_mask.sum()
    
    no_entregados_count = len(con_emo_df) - entregados_count
    
    return pd.Series({'EMOs entregados en el mes': entregados_count, 'Total de EMOs pendientes': no_entregados_count})


# --- HELPERS DE TEXTO NUEVOS (para C, D, E, F) ---
def _series_to_breakdown_text(prefix: str, s: pd.Series) -> str:
    if s is None or len(s) == 0:
        return f"{prefix}: Sin datos."
    total = int(s.sum())
    if total <= 0:
        return f"{prefix}: Sin datos."
    parts = [f"{k}: {int(v)} ({(int(v)/total)*100:.1f}%)" for k, v in s.items()]
    return f"{prefix}: " + ", ".join(parts) + "."


def generate_text_C1(data: pd.Series) -> str:
    return _series_to_breakdown_text("Cobertura general de EMOs", data)


def generate_text_C2(data: pd.Series) -> str:
    return _series_to_breakdown_text("Entrega de EMOs en el mes", data)


def generate_text_D(data_d) -> str:
    # apartado_d suele venir como dict con "totals"
    if isinstance(data_d, dict) and "totals" in data_d:
        return _series_to_breakdown_text("Distribución por perfiles de EMO", data_d["totals"])
    if isinstance(data_d, pd.Series):
        return _series_to_breakdown_text("Distribución por perfiles de EMO", data_d)
    return "Distribución por perfiles de EMO: Sin datos."


def generate_text_E(data_e: pd.Series) -> str:
    return _series_to_breakdown_text("Vigencia de EMO", data_e)


def generate_text_F(data_f) -> str:
    # apartado_f suele venir como dict con "counts_total"
    if isinstance(data_f, dict) and "counts_total" in data_f:
        return _series_to_breakdown_text("Aptitud de EMO (total)", data_f["counts_total"])
    if isinstance(data_f, pd.Series):
        return _series_to_breakdown_text("Aptitud de EMO (total)", data_f)
    return "Aptitud de EMO (total): Sin datos."


def calculate_all_statistics(df_active: pd.DataFrame, df_all_trab: pd.DataFrame, year: int, month: int) -> dict:
    """Calcula todas las estadísticas para el reporte."""
    stats = {
        'apartado_a': calculate_stats_A_epidemiology(df_active),
        'apartado_b': calculate_stats_B_age_group(df_active),
        'apartado_c1': calculate_stats_C1_cobertura(df_all_trab),
        'apartado_c2': calculate_stats_C2_entrega_mes(df_all_trab, year, month),
        # Las siguientes funciones también deberían usar los nombres internos
        'apartado_d': emo_domain.calculate_stats_D_emo_profiles(df_active),
        'apartado_e': emo_domain.calculate_stats_E_emo_validity(df_active),
        'apartado_f': emo_domain.calculate_stats_F_aptitude(df_active),
    }
    return stats