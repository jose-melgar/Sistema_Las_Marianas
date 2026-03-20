"""
Módulo de Lógica de Negocio para el Reporte Estándar.

Contiene las funciones para calcular todas las estadísticas necesarias.
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

def calculate_all_statistics(df_active: pd.DataFrame) -> dict:
    """
    Calcula todas las estadísticas para el reporte y las devuelve en un diccionario.
    """
    stats = {
        'apartado_a': emo_domain.calculate_stats_A_epidemiology(df_active),
        'apartado_b': emo_domain.calculate_stats_B_age_group(df_active),
        'apartado_c': emo_domain.calculate_stats_C_emo_status(df_active),
        'apartado_d': emo_domain.calculate_stats_D_emo_profiles(df_active),
        'apartado_e': emo_domain.calculate_stats_E_emo_validity(df_active),
        'apartado_f': emo_domain.calculate_stats_F_aptitude(df_active),
    }
    return stats