"""
utils/loader.py (v1.0.8)
Loader basado en esquemas por hoja para soportar distintas distribuciones.

Soporta:
- listado de hojas
- lectura raw para Análisis (respeta header especial de Registro EMO)
- carga normalizada para informes (estadísticas)

Requisitos de Informe:
- Selección de Obra desde Trabajadores.Planta
- Cruces por DNI (normalizado)
- Trabajador Activo según Historial_Trabajadores.FechaSalida (vacía o posterior a mes/año consultados)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import warnings
import pandas as pd


DEFAULT_EXCEL_PATH = Path("data") / "Base de Datos Estela 1.0.8.xlsm"


def _install_warning_filters() -> None:
    warnings.filterwarnings(
        "ignore",
        message=r".*Data Validation extension is not supported.*",
        category=UserWarning,
        module=r"openpyxl\..*",
    )


SHEET_HEADER_ROW: dict[str, int] = {
    "Registro EMO": 11,  # headers desde fila 12
}

SHEET_SCHEMAS: dict[str, dict[str, str]] = {
    # Para informes actuales no necesitamos Accidentes aquí (puede mantenerse para otros módulos)
    "Trabajadores": {
        "Planta": "obra",         # Obra/Proyecto real
        "FechaIngreso": "fecha_ingreso",
        "DNI": "dni",             # puede ser DNI o dni (fallback en _read_normalized)
        "Edad": "edad",
        "Sexo": "sexo",
        "Perfil": "perfil",
        "Vigencia": "vigencia",
        "APTITUD": "aptitud",
        "Nombre": "nombre",
    },
    "Historial_Trabajadores": {
        "DNI": "dni",             # col A en tu mapeo
        "Obra": "obra",
        "FechaIngreso": "fecha_ingreso",
        "FechaSalida": "fecha_salida",
    },
    "Registro EMO": {
        "NOMBRE": "nombre",
        "DNI": "dni",
        "FECHA": "fecha_emo",
        "FECHA ENTREGA": "fecha_entrega",
    },
}


@dataclass
class EstelaData:
    trabajadores: pd.DataFrame
    historial_trabajadores: pd.DataFrame
    registro_emo: pd.DataFrame
    meta: Dict[str, Any]


class ExcelLoader:
    def __init__(self, excel_path: Path = DEFAULT_EXCEL_PATH):
        self.excel_path = Path(excel_path)
        self._cache: Optional[EstelaData] = None
        self._last_mtime: Optional[float] = None
        self._sheet_names_cache: Optional[List[str]] = None

    def _get_mtime(self) -> float:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo Excel en: {self.excel_path.resolve()}")
        return self.excel_path.stat().st_mtime

    def get_sheet_names(self, force: bool = False) -> List[str]:
        _install_warning_filters()
        current_mtime = self._get_mtime()

        if self._sheet_names_cache is not None and not force and self._last_mtime == current_mtime:
            return self._sheet_names_cache

        xls = pd.ExcelFile(self.excel_path, engine="openpyxl")
        self._sheet_names_cache = list(xls.sheet_names)
        return self._sheet_names_cache

    @staticmethod
    def excel_col_letter(idx_zero_based: int) -> str:
        n = idx_zero_based + 1
        letters = ""
        while n:
            n, rem = divmod(n - 1, 26)
            letters = chr(65 + rem) + letters
        return letters

    def _header_row_for(self, sheet_name: str) -> int:
        return SHEET_HEADER_ROW.get(sheet_name, 0)

    def read_sheet_raw(self, sheet_name: str) -> pd.DataFrame:
        _install_warning_filters()
        header_row = self._header_row_for(sheet_name)
        return pd.read_excel(self.excel_path, sheet_name=sheet_name, engine="openpyxl", header=header_row)

    @staticmethod
    def _normalize_dni(series: pd.Series) -> pd.Series:
        s = series.astype("string")
        s = s.str.strip()
        s = s.str.replace(r"\s+", "", regex=True)
        s = s.str.replace(r"\.0$", "", regex=True)
        s = s.replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
        return s

    def _read_sheet_with_dtype(self, sheet_name: str, header_row: int, dtype: dict | None) -> pd.DataFrame:
        return pd.read_excel(
            self.excel_path,
            sheet_name=sheet_name,
            engine="openpyxl",
            header=header_row,
            dtype=dtype if dtype else None,
        )

    def _read_normalized(self, sheet_name: str) -> pd.DataFrame:
        schema = SHEET_SCHEMAS[sheet_name].copy()
        header_row = self._header_row_for(sheet_name)

        df = self._read_sheet_with_dtype(sheet_name, header_row, dtype=None)

        # Alias: DNI vs dni (si alguna hoja lo cambia)
        if "DNI" not in df.columns and "dni" in df.columns and "DNI" in schema:
            schema.pop("DNI", None)
            schema["dni"] = "dni"

        dtype: dict[str, str] = {}
        if "DNI" in schema:
            dtype["DNI"] = "string"
        if "dni" in schema:
            dtype["dni"] = "string"

        if dtype:
            df = self._read_sheet_with_dtype(sheet_name, header_row, dtype=dtype)

        missing = [col for col in schema.keys() if col not in df.columns]
        if missing:
            raise ValueError(
                f"Faltan columnas requeridas en hoja '{sheet_name}': {missing}. "
                f"Columnas disponibles: {list(df.columns)}"
            )

        df = df[list(schema.keys())].rename(columns=schema).copy()

        # Normalizaciones
        if "dni" in df.columns:
            df["dni"] = self._normalize_dni(df["dni"])

        # Fechas
        for col in ["fecha_ingreso", "fecha_salida", "fecha_emo", "fecha_entrega"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        # Texto
        for col in ["obra", "sexo", "perfil", "vigencia", "aptitud", "nombre"]:
            if col in df.columns:
                df[col] = df[col].astype("string").str.strip()
                df.loc[df[col].isin(["nan", "None", ""]), col] = pd.NA

        # Edad numérica
        if "edad" in df.columns:
            df["edad"] = pd.to_numeric(df["edad"], errors="coerce")

        return df

    def load(self, force: bool = False) -> EstelaData:
        _install_warning_filters()
        current_mtime = self._get_mtime()

        if self._cache is not None and not force and self._last_mtime == current_mtime:
            return self._cache

        trabajadores = self._read_normalized("Trabajadores")
        historial = self._read_normalized("Historial_Trabajadores")
        registro_emo = self._read_normalized("Registro EMO")

        meta = {
            "excel_path": str(self.excel_path),
            "mtime": current_mtime,
            "rows": {
                "trabajadores": int(len(trabajadores)),
                "historial_trabajadores": int(len(historial)),
                "registro_emo": int(len(registro_emo)),
            },
        }

        self._cache = EstelaData(
            trabajadores=trabajadores,
            historial_trabajadores=historial,
            registro_emo=registro_emo,
            meta=meta,
        )
        self._last_mtime = current_mtime
        return self._cache

    def reload_if_changed(self) -> Tuple[EstelaData, bool]:
        current_mtime = self._get_mtime()
        if self._last_mtime is None or self._last_mtime != current_mtime:
            return self.load(force=True), True
        return self.load(force=False), False