"""
Auditoría (solo lectura):
- faltantes: detecta valores faltantes en columnas clave por hoja
- duplicados: detecta duplicados por llaves definidas por hoja

NOTA: No modifica el Excel; el usuario corrige manualmente en el archivo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from utils.loader import ExcelLoader
from utils.formatting import format_cell

NEON = "bright_green"


# Reglas mínimas (puedes ajustar/expandir cuando quieras)
AUDIT_REQUIRED_COLUMNS: dict[str, list[str]] = {
    "Trabajadores": ["DNI", "Nombre", "Sexo", "Edad", "Planta"],
    "Accidentes": ["DNI", "Fecha", "ParteCuerpo"],
    "Historial_Trabajadores": ["DNI", "Obra", "FechaIngreso"],
    "Registro EMO": ["NOMBRE", "DNI", "FECHA"],
}

AUDIT_DUPLICATE_KEYS: dict[str, list[str]] = {
    "Trabajadores": ["DNI"],
    "Accidentes": ["AccidenteID"],          # si no existiera, luego lo ajustamos a ["DNI", "Fecha"]
    "Historial_Trabajadores": ["DNI", "Obra", "FechaIngreso"],
    "Registro EMO": ["NOMBRE"],             # requisito tuyo: únicos por NOMBRE
}


def _is_missing_value(x) -> bool:
    if x is None:
        return True
    s = str(x).strip()
    return s in ("", "nan", "None", "<NA>", "NaT")


def _sheet_header_row(loader: ExcelLoader, sheet: str) -> int:
    # usando el mismo criterio del loader (Registro EMO header fila 12)
    # accedemos al método privado por consistencia: replicamos la regla aquí
    return 11 if sheet == "Registro EMO" else 0


def _read_sheet_for_audit(loader: ExcelLoader, sheet: str) -> pd.DataFrame:
    header_row = _sheet_header_row(loader, sheet)
    return pd.read_excel(loader.excel_path, sheet_name=sheet, engine="openpyxl", header=header_row)


def _print_summary_table(console: Console, rows: list[dict], title: str) -> None:
    t = Table(title=title, header_style=f"bold {NEON}")
    if not rows:
        console.print(Panel("No se encontraron hallazgos.", border_style=NEON))
        return

    cols = list(rows[0].keys())
    for c in cols:
        t.add_column(str(c), style=NEON, overflow="fold")

    for r in rows:
        t.add_row(*[format_cell(r.get(c), str(c)) for c in cols])

    console.print(t)


def auditoria_faltantes(console: Console, loader: ExcelLoader) -> None:
    console.print(Panel("Auditoría: Valores faltantes (solo lectura)", border_style=NEON))

    sheets = loader.get_sheet_names()
    enabled = [s for s in AUDIT_REQUIRED_COLUMNS.keys() if s in sheets]

    if not enabled:
        console.print(Panel("No se encontraron hojas configuradas para auditoría.", border_style="yellow"))
        return

    # resumen
    summary_rows: list[dict] = []
    details: list[dict] = []

    for sheet in enabled:
        df = _read_sheet_for_audit(loader, sheet)
        required = [c for c in AUDIT_REQUIRED_COLUMNS[sheet] if c in df.columns]

        # Si una columna requerida no existe, eso también es hallazgo
        missing_cols = [c for c in AUDIT_REQUIRED_COLUMNS[sheet] if c not in df.columns]
        for mc in missing_cols:
            summary_rows.append({"Hoja": sheet, "Columna": mc, "Faltantes": "COLUMNA NO EXISTE"})

        if df.empty:
            continue

        for col in required:
            mask = df[col].apply(_is_missing_value)
            cnt = int(mask.sum())
            if cnt > 0:
                summary_rows.append({"Hoja": sheet, "Columna": col, "Faltantes": cnt})

                # Guardar ejemplos (fila excel = index + header_row + 2)
                header_row = _sheet_header_row(loader, sheet)
                sample_idx = df.index[mask].tolist()[:50]  # guardamos algunos
                id_col = "DNI" if "DNI" in df.columns else ("dni" if "dni" in df.columns else None)

                for i in sample_idx:
                    excel_row = int(i) + header_row + 2  # +2: header en 1 y data arranca en 2
                    details.append(
                        {
                            "Hoja": sheet,
                            "FilaExcel": excel_row,
                            "Columna": col,
                            "Identificador": df.loc[i, id_col] if id_col else "",
                        }
                    )

    _print_summary_table(console, summary_rows, "Resumen de faltantes")

    if not details:
        return

    ver = Prompt.ask("[cyan]¿Ver detalle de filas con faltantes? (si/no)[/cyan]").strip().lower()
    if ver not in ("si", "s", "yes", "y"):
        return

    n = IntPrompt.ask("[cyan]¿Cuántas filas de detalle mostrar? (ej: 30)[/cyan]", default=30)
    n = max(1, min(int(n), len(details)))

    _print_summary_table(console, details[:n], f"Detalle (primeros {n}) — Corrige manualmente en Excel")


def auditoria_duplicados(console: Console, loader: ExcelLoader) -> None:
    console.print(Panel("Auditoría: Duplicados (solo lectura)", border_style=NEON))

    sheets = loader.get_sheet_names()
    enabled = [s for s in AUDIT_DUPLICATE_KEYS.keys() if s in sheets]

    if not enabled:
        console.print(Panel("No se encontraron hojas configuradas para auditoría.", border_style="yellow"))
        return

    summary_rows: list[dict] = []

    for sheet in enabled:
        df = _read_sheet_for_audit(loader, sheet)
        keys = AUDIT_DUPLICATE_KEYS[sheet]

        # si faltan columnas llave, reportar
        missing_keys = [k for k in keys if k not in df.columns]
        if missing_keys:
            summary_rows.append(
                {"Hoja": sheet, "Llave": ", ".join(keys), "Duplicados": "NO SE PUEDE (faltan columnas llave)"}
            )
            continue

        if df.empty:
            summary_rows.append({"Hoja": sheet, "Llave": ", ".join(keys), "Duplicados": 0})
            continue

        dup_mask = df.duplicated(subset=keys, keep=False)
        dup_count = int(dup_mask.sum())
        summary_rows.append({"Hoja": sheet, "Llave": ", ".join(keys), "Duplicados": dup_count})

        if dup_count > 0:
            # Mostrar top grupos duplicados
            grp = df.loc[dup_mask, keys].astype(str).value_counts().head(10)
            t = Table(title=f"Top duplicados :: {sheet}", header_style=f"bold {NEON}")
            t.add_column("Clave", style=NEON)
            t.add_column("Conteo", style=NEON, justify="right")
            for k, v in grp.items():
                # k puede ser tuple si hay varias keys
                k_str = " | ".join(k) if isinstance(k, tuple) else str(k)
                t.add_row(k_str, str(int(v)))
            console.print(t)

    _print_summary_table(console, summary_rows, "Resumen de duplicados")


def run_auditoria(console: Console, loader: ExcelLoader) -> None:
    while True:
        console.print(
            Panel(
                "[bold bright_green]AUDITORÍA (Análisis)[/bold bright_green]\n"
                "- faltantes\n"
                "- duplicados\n"
                "- menu",
                border_style=NEON,
            )
        )
        cmd = Prompt.ask("[cyan]Selecciona opción[/cyan]").strip().lower()
        if cmd == "menu":
            return
        if cmd == "faltantes":
            auditoria_faltantes(console, loader)
            continue
        if cmd == "duplicados":
            auditoria_duplicados(console, loader)
            continue

        console.print(Panel("Opción no válida.", border_style="yellow"))