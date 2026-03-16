"""
Módulo para la auditoría de datos.

Realiza verificaciones de calidad de los datos cargados, como la
detección de valores faltantes y registros duplicados, basado en las
reglas definidas en la configuración del loader.
"""
from typing import Dict, List, Tuple
import pandas as pd

from las_marianas_so.loader.config import SYSTEM_CONFIG

def find_duplicates(df: pd.DataFrame, key_columns: List[str]) -> pd.DataFrame:
    """
    Encuentra filas duplicadas en un DataFrame basado en una lista de columnas clave.
    
    Args:
        df (pd.DataFrame): El DataFrame a verificar.
        key_columns (List[str]): Lista de nombres de columnas que definen un registro único.

    Returns:
        pd.DataFrame: Un DataFrame que contiene solo las filas duplicadas.
    """
    if not all(col in df.columns for col in key_columns):
        # Si alguna columna clave no existe, no se puede verificar duplicados.
        return pd.DataFrame()
        
    duplicates = df[df.duplicated(subset=key_columns, keep=False)]
    return duplicates.sort_values(by=key_columns)

def find_missing_values(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, pd.Series]:
    """
    Encuentra filas con valores faltantes en columnas requeridas.
    
    Args:
        df (pd.DataFrame): El DataFrame a verificar.
        required_columns (List[str]): Columnas que no deben tener valores nulos.

    Returns:
        Dict[str, pd.Series]: Un diccionario donde cada clave es el nombre de una
                              columna y el valor es una Serie de los índices de las
                              filas con valores faltantes en esa columna.
    """
    missing_data_indices = {}
    for col in required_columns:
        if col in df.columns:
            missing_indices = df[df[col].isnull() | (df[col] == '')].index
            if not missing_indices.empty:
                missing_data_indices[col] = missing_indices
    return missing_data_indices

def run_audit(data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    """
    Ejecuta la auditoría completa sobre todos los DataFrames cargados.

    Args:
        data (Dict[str, pd.DataFrame]): Diccionario de DataFrames del ExcelLoader.

    Returns:
        Dict[str, Dict]: Resultados de la auditoría, organizados por hoja.
    """
    audit_results = {}
    sheet_configs = SYSTEM_CONFIG.get("sheets", {})

    for df_alias, df in data.items():
        config = sheet_configs.get(df_alias, {})
        key_columns = config.get('unique_key', [])
        required_columns = list(config.get('columns', {}).values()) # Todos las columnas definidas son requeridas
        
        duplicates_df = pd.DataFrame()
        if key_columns:
            duplicates_df = find_duplicates(df, key_columns)

        missing_map = find_missing_values(df, required_columns)

        if not duplicates_df.empty or missing_map:
            audit_results[df_alias] = {
                'duplicates': duplicates_df,
                'missing': missing_map,
                'header_row': config.get('header_row', 0)
            }
            
    return audit_results