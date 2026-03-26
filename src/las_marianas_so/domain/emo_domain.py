"""
Lógica de Dominio para el Análisis de EMOs.

Contiene las funciones de negocio para calcular las estadísticas
requeridas por los informes EMO, como la definición de trabajadores
activos y los cálculos para los apartados A-F.
"""
import pandas as pd
from datetime import datetime

def get_active_workers(
    df_trabajadores: pd.DataFrame,
    df_historial: pd.DataFrame,
    obra: str,
    year: int,
    month: int
) -> pd.DataFrame:
    """
    Determina los trabajadores activos en una obra y fecha específicas.

    Un trabajador se considera activo si:
    1. Su fecha de ingreso es anterior o igual al fin del mes consultado.
    2. No tiene fecha de salida, O su fecha de salida es posterior al fin del mes.
    """
    end_of_month = datetime(year, month, 1) + pd.offsets.MonthEnd(0)
    
    # Filtrar historial por la obra de interés
    historial_obra = df_historial[df_historial['obra'] == obra].copy()
    
    # Identificar el último estado de cada trabajador en esa obra
    historial_obra['fecha_ingreso'] = pd.to_datetime(historial_obra['fecha_ingreso'])
    historial_obra['fecha_salida'] = pd.to_datetime(historial_obra['fecha_salida'])
    
    latest_records = historial_obra.sort_values('fecha_ingreso').groupby('dni').last()
    
    # Filtrar activos
    active_mask = (
        (latest_records['fecha_ingreso'] <= end_of_month) &
        (latest_records['fecha_salida'].isnull() | (latest_records['fecha_salida'] > end_of_month))
    )
    active_dnis = latest_records[active_mask].index
    
    # Devolver los datos completos de los trabajadores activos
    return df_trabajadores[df_trabajadores['dni'].isin(active_dnis)].copy()


def calculate_stats_A_epidemiology(df_active: pd.DataFrame) -> pd.Series:
    """Calcula la distribución por sexo (Apartado A)."""
    return df_active['sexo'].value_counts()

def calculate_stats_B_age_group(df_active: pd.DataFrame) -> pd.Series:
    """Calcula la distribución por grupo etario (Apartado B)."""
    bins = [0, 18, 25, 35, 45, 55, 100]
    labels = ['<18', '18-24', '25-34', '35-44', '45-54', '55+']
    df_active['grupo_etario'] = pd.cut(df_active['edad'], bins=bins, labels=labels, right=False)
    return df_active['grupo_etario'].value_counts().sort_index()

def calculate_stats_C_emo_status(df_active: pd.DataFrame) -> pd.Series:
    """Calcula el estatus de EMO (con/sin) (Apartado C)."""
    df_active['tiene_emo'] = df_active['ultimo_emo'].notna().map({True: 'Con EMO', False: 'Sin EMO'})
    return df_active['tiene_emo'].value_counts()

def calculate_stats_D_emo_profiles(df_active: pd.DataFrame) -> pd.Series:
    """Calcula la distribución por perfiles de EMO (Apartado D)."""
    return df_active['perfil'].value_counts()

def calculate_stats_E_emo_validity(df_active: pd.DataFrame) -> pd.Series:
    """Calcula la vigencia de los EMOs (Apartado E)."""
    df_active['vigencia_emo'] = 'No Aplica'
    mask_vigente = df_active['vigencia'].notna()
    df_active.loc[mask_vigente, 'vigencia_emo'] = df_active.loc[mask_vigente, 'vigencia'].apply(
        lambda x: 'Vigente' if 'vigente' in str(x).lower() else 'Vencido'
    )
    return df_active['vigencia_emo'].value_counts()

def calculate_stats_F_aptitude(df_active: pd.DataFrame) -> dict:
    """Calcula la distribución de aptitud (Apartado F) segmentado por sexo y con alias normalizados."""
    order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]
    alias_map = {
        "APTO CON RESTRICCIÓN": "CON RESTRICCIONES",
        "APTO CON RESTRICCION": "CON RESTRICCIONES",
        "CON RESTRICCION": "CON RESTRICCIONES",
        "CON RESTRICCIONES": "CON RESTRICCIONES",
        "NO APTO": "NO APTO",
        "OBSERVADO": "OBSERVADO",
        "APTO": "APTO",
    }
    
    # Si no hay datos, devolver diccionarios con ceros
    if 'aptitud' not in df_active.columns or df_active.empty:
        empty_s = pd.Series([0]*len(order), index=order, dtype=int)
        return {"counts_total": empty_s, "counts_f": empty_s, "counts_m": empty_s}

    df = df_active.copy()
    
    # 1. Normalizar la columna aptitud para TODO el DataFrame
    df["_apt_norm"] = df["aptitud"].apply(
        lambda v: str(v).strip().upper() if pd.notna(v) else ""
    ).replace(alias_map)
    
    # 2. Calcular el total usando la data ya limpia
    counts_total = df["_apt_norm"].value_counts().reindex(order).fillna(0).astype(int)
    
    # 3. Calcular la segmentación por sexo
    if "sexo" in df.columns:
        df["_sexo_norm"] = df["sexo"].apply(
            lambda v: str(v).strip().upper() if pd.notna(v) else ""
        )
        counts_f = df[df["_sexo_norm"] == "F"]["_apt_norm"].value_counts().reindex(order).fillna(0).astype(int)
        counts_m = df[df["_sexo_norm"] == "M"]["_apt_norm"].value_counts().reindex(order).fillna(0).astype(int)
    else:
        empty_s = pd.Series([0]*len(order), index=order, dtype=int)
        counts_f, counts_m = empty_s, empty_s
        
    # Retornar el diccionario completo
    return {
        "counts_total": counts_total,
        "counts_f": counts_f,
        "counts_m": counts_m
    }