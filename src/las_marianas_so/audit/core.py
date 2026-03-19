"""
Módulo para la auditoría de datos.

Realiza verificaciones de calidad de los datos cargados, como la
detección de valores faltantes, basado en las reglas definidas 
en la configuración del loader.
"""
from typing import Dict, List, Tuple
import pandas as pd

from las_marianas_so.loader.config import SYSTEM_CONFIG

def find_missing_values(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, int]:
    """
    Encuentra la cantidad de valores faltantes en columnas requeridas.
    
    Args:
        df (pd.DataFrame): El DataFrame a verificar.
        required_columns (List[str]): Columnas que no deben tener valores nulos.

    Returns:
        Dict[str, int]: Un diccionario donde cada clave es el nombre de una
                        columna con faltantes y el valor es la cantidad de
                        registros faltantes.
    """
    missing_data_counts = {}
    for col in required_columns:
        if col in df.columns:
            # Contamos los valores nulos o strings vacíos en la columna
            missing_count = df[col].isnull().sum() + (df[col] == '').sum()
            if missing_count > 0:
                missing_data_counts[col] = missing_count
    return missing_data_counts

def run_audit_on_sheet(df: pd.DataFrame, df_alias: str) -> Dict[str, int]:
    """
    Ejecuta la auditoría de valores faltantes en un único DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame de la hoja seleccionada.
        df_alias (str): El alias de la hoja (ej: 'trabajadores').

    Returns:
        Dict[str, int]: Resultados de la auditoría (conteo de faltantes por columna).
    """
    sheet_configs = SYSTEM_CONFIG.get("sheets", {})
    config = sheet_configs.get(df_alias, {})
    
    # Todas las columnas definidas en el config se consideran requeridas
    required_columns = list(config.get('columns', {}).values())
    
    missing_summary = find_missing_values(df, required_columns)
            
    return missing_summary