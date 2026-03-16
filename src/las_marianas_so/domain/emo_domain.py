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

def calculate_stats_F_aptitude(df_active: pd.DataFrame) -> pd.Series:
    """Calcula la distribución de aptitud (Apartado F)."""
    return df_active['aptitud'].value_counts()