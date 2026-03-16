"""
Core del sistema de carga de datos (Excel Loader).

Este módulo contiene la clase `ExcelLoader`, responsable de leer el archivo
Excel principal, procesar las hojas según la configuración centralizada,
y proveer DataFrames limpios y normalizados al resto de la aplicación.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

from .config import SYSTEM_CONFIG

class ExcelLoader:
    """
    Cargador de datos centralizado desde un archivo Excel.

    Lee la configuración desde `config/loader.config.yml` para determinar qué
    hojas cargar, qué columnas seleccionar, cómo renombrarlas y qué
    reglas de normalización aplicar.
    """

    def __init__(self, base_path: Path):
        """
        Inicializa el loader.

        Args:
            base_path (Path): La ruta base del proyecto, usada para resolver
                              la ruta del archivo Excel.
        """
        self.config = SYSTEM_CONFIG
        excel_path_str = self.config.get("excel_file_path")
        if not excel_path_str:
            raise ValueError("La clave 'excel_file_path' no está definida en la configuración.")

        self.excel_path = base_path / excel_path_str
        self.data: Dict[str, pd.DataFrame] = {}
        self._load_all_sheets()

    def _normalize_dni(self, series: pd.Series) -> pd.Series:
        """Normaliza una columna de DNI a string, eliminando '.0' y espacios."""
        return series.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

    def _apply_normalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica las reglas de normalización definidas en la configuración.
        """
        rules = self.config.get("normalization_rules", {})
        
        # Limpieza de columnas de texto/string (ej: DNI)
        string_cols = rules.get("string_cleanup_columns", [])
        for col in string_cols:
            if col in df.columns:
                df[col] = self._normalize_dni(df[col])

        # Parseo de columnas de fecha
        date_cols = rules.get("date_columns", [])
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        
        return df

    def _load_sheet(self, sheet_config: Dict[str, Any]) -> pd.DataFrame:
        """
        Carga, limpia y normaliza una única hoja de Excel.
        """
        sheet_name = sheet_config['name']
        header_row = sheet_config['header_row']
        columns_map = sheet_config['columns']
        
        try:
            df = pd.read_excel(
                self.excel_path,
                sheet_name=sheet_name,
                header=header_row
            )
        except Exception as e:
            raise IOError(f"Error al leer la hoja '{sheet_name}' de '{self.excel_path}'. Detalles: {e}")

        # Filtrar y renombrar columnas
        relevant_cols = list(columns_map.keys())
        missing_cols = [col for col in relevant_cols if col not in df.columns]
        if missing_cols:
            # Advertencia en lugar de error para flexibilidad
            print(f"ADVERTENCIA: En la hoja '{sheet_name}', las siguientes columnas no se encontraron y serán ignoradas: {missing_cols}")
            relevant_cols = [col for col in relevant_cols if col in df.columns]

        df = df[relevant_cols]
        df = df.rename(columns={k: v for k, v in columns_map.items() if k in relevant_cols})
        
        # Aplicar normalización general
        df = self._apply_normalization(df)

        return df

    def _load_all_sheets(self):
        """
        Orquesta la carga de todas las hojas definidas en la configuración.
        """
        print("Iniciando carga de datos desde Excel...")
        sheets_to_load = self.config.get("sheets", {})
        if not sheets_to_load:
            raise ValueError("No hay hojas definidas para cargar en 'config/loader.config.yml'.")

        for df_alias, sheet_config in sheets_to_load.items():
            print(f"  - Cargando hoja: '{sheet_config['name']}' -> como '{df_alias}'")
            self.data[df_alias] = self._load_sheet(sheet_config)
        
        print("Carga de datos completada exitosamente.")

    def get_data(self) -> Dict[str, pd.DataFrame]:
        """Retorna el diccionario de DataFrames cargados."""
        return self.data