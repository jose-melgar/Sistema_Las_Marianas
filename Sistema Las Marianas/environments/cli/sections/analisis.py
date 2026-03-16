"""
Sección Análisis:
- Ver datos (como antes)
- Auditoría (faltantes/duplicados) para agilizar correcciones manuales en Excel
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from utils.loader import ExcelLoader
from utils.formatting import format_cell
from environments.cli.sections.auditoria import run_auditoria

NEON = "bright_green"


def _print_sheet_list(console: Console, sheets: list[str]) -> None:
    table = Table(title="Hojas disponibles", header_style=f"bold {NEON}")
    table.add_column("Nombre de hoja", style=NEON)
    for s in sheets:
        table.add_row(s)
    console.print(table)


def _columns_table(loader: ExcelLoader, df) -> Table:
    table = Table(title="Columnas (con letra Excel)", header_style=f"bold {NEON}")
    table.add_column("Letra", style=NEON, width=6)
    table.add_column("Columna", style=NEON)
    for i, col in enumerate(df.columns):
        table.add_row(loader.excel_col_letter(i), str(col))
    return table


def _df_to_rich_table(df, title: str, max_rows: int = 50) -> Table:
    table = Table(title=title, header_style=f"bold {NEON}", show_lines=False)
    for col in df.columns:
        table.add_column(str(col), style=NEON, overflow="fold")

    view = df.head(max_rows)
    for _, row in view.iterrows():
        table.add_row(*[format_cell(row[c], str(c)) for c in df.columns])

    return table


def _letters_to_indices(letters: list[str]) -> list[int]:
    indices: list[int] = []
    for L in letters:
        idx = 0
        for ch in L:
            if not ("A" <= ch <= "Z"):
                raise ValueError(f"Letra inválida: {L}")
            idx = idx * 26 + (ord(ch) - 64)
        indices.append(idx - 1)
    return indices


def _run_ver_datos(console: Console, loader: ExcelLoader) -> None:
    sheets = loader.get_sheet_names()

    while True:
        _print_sheet_list(console, sheets)
        hoja = Prompt.ask("[cyan]Selecciona una hoja por nombre ('menu' para volver)[/cyan]").strip()
        if hoja.lower() == "menu":
            return

        if hoja not in sheets:
            console.print(Panel("Hoja no encontrada. Intenta nuevamente.", border_style="yellow"))
            continue

        df = loader.read_sheet_raw(hoja)
        console.print(_columns_table(loader, df))

        while True:
            sel = Prompt.ask(
                "[cyan]Ingresa letras (ej: A-D-F), 'todas' para todas, o 'menu'[/cyan]"
            ).strip()

            if sel.lower() == "menu":
                return

            if sel.lower() == "todas":
                console.print(_df_to_rich_table(df, title=f"{hoja} (todas las columnas)", max_rows=50))
                break

            letras = [x.strip().upper() for x in sel.split("-") if x.strip()]
            if not letras:
                console.print(Panel("Entrada vacía.", border_style="yellow"))
                continue

            try:
                indices = _letters_to_indices(letras)
                view = df.iloc[:, indices]
            except ValueError as e:
                console.print(Panel(str(e), border_style="yellow"))
                continue
            except Exception:
                console.print(Panel("Selección fuera de rango. Revisa letras.", border_style="yellow"))
                continue

            console.print(_df_to_rich_table(view, title=f"{hoja} (columnas: {', '.join(letras)})", max_rows=50))
            break


def run_analisis(console: Console, loader: ExcelLoader) -> None:
    while True:
        console.print(
            Panel(
                "[bold bright_green]ANÁLISIS[/bold bright_green]\n"
                "- ver\n"
                "- auditoria\n"
                "- menu",
                border_style=NEON,
            )
        )
        cmd = Prompt.ask("[cyan]Selecciona opción[/cyan]").strip().lower()
        if cmd == "menu":
            return
        if cmd == "ver":
            _run_ver_datos(console, loader)
            continue
        if cmd == "auditoria":
            run_auditoria(console, loader)
            continue

        console.print(Panel("Opción no válida.", border_style="yellow"))