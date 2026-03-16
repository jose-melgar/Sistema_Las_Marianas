"""
utils/formatting.py
Formateo para impresión en consola.

Regla corregida:
- Solo se aplica formato DNI (8 dígitos, zfill) cuando el nombre de la columna indica DNI.
- Para otras columnas numéricas (conteos, edades, etc.) se imprime normal como int/float.
"""

from __future__ import annotations

import math
import re
from typing import Any

_DNI_RE = re.compile(r"^\d{1,8}$")

# Columnas que se deben tratar como DNI (normalizado)
DNI_COLUMN_NAMES = {
    "dni",
    "dni trabajador",
    "dni_trabajador",
    "documento",
    "documentoid",
    "documento_id",
    "nrodocumento",
    "nro_documento",
}


def _is_dni_column(column_name: str | None) -> bool:
    if not column_name:
        return False
    c = str(column_name).strip().lower()
    return c in DNI_COLUMN_NAMES


def format_dni_value(value: Any) -> str:
    """Formatea un DNI como string de 8 dígitos si parece numérico."""
    if value is None:
        return ""

    s = str(value).strip()
    if s in ("<NA>", "nan", "NaT", "None", ""):
        return ""

    # "12345678.0"
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]

    # numérico puro
    if s.isdigit() and _DNI_RE.match(s):
        return s.zfill(8)

    # floats/ints raros -> intentar
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if value.is_integer():
            s2 = str(int(value))
            if _DNI_RE.match(s2):
                return s2.zfill(8)

    if isinstance(value, int):
        s2 = str(value)
        if _DNI_RE.match(s2):
            return s2.zfill(8)

    return s


def format_cell(value: Any, column_name: str | None = None) -> str:
    """
    Formatea una celda según el tipo de columna.

    - Si es columna DNI -> formatea como DNI de 8 dígitos (string)
    - Si es número (conteos, edades) -> imprime como int si aplica
    - Caso general -> str(value)
    """
    if value is None:
        return ""

    s = str(value).strip()
    if s in ("<NA>", "nan", "NaT", "None", ""):
        return ""

    # DNI solo por nombre de columna
    if _is_dni_column(column_name):
        return format_dni_value(value)

    # Números: evitar "1.0"
    if isinstance(value, (int,)):
        return str(value)

    if isinstance(value, (float,)):
        if math.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
        return str(value)

    return s