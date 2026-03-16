"""
Router CLI principal (Las Marianas-SO).
Menú principal por texto y submenús por secciones.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from utils.loader import ExcelLoader, DEFAULT_EXCEL_PATH
from environments.cli.sections.analisis import run_analisis
from environments.cli.sections.estadisticas import run_estadisticas
from environments.cli.sections.dashboards import run_dashboards
from environments.cli.sections.matriz_riesgos import run_matriz_riesgos
from environments.cli.sections.modelo_predictivo import run_modelo_predictivo


NEON = "bright_green"
APP_TITLE = "Las Marianas-SO :: Consultorio Médico (CLI)"
PROMPT = "Las Marianas-SO>"


def _title_bar(text: str) -> Panel:
    t = Text(text, style=f"bold {NEON}")
    return Panel(t, border_style=NEON)


def _menu_principal_panel() -> Panel:
    contenido = (
        "[bold bright_green]Menú principal[/bold bright_green]\n"
        "- [cyan]analisis[/cyan]\n"
        "- [cyan]estadisticas[/cyan]\n"
        "- [cyan]dashboards[/cyan] (próximamente)\n"
        "- [cyan]matriz de riesgos[/cyan] (próximamente)\n"
        "- [cyan]modelo predictivo[/cyan] (próximamente)\n\n"
        "Comandos:\n"
        "- [cyan]clear[/cyan]\n"
        "- [cyan]exit[/cyan]\n"
    )
    return Panel(contenido, border_style=NEON)


def run() -> int:
    console = Console()
    console.clear()
    console.print(_title_bar(APP_TITLE))

    loader = ExcelLoader(DEFAULT_EXCEL_PATH)
    try:
        data = loader.load()
    except FileNotFoundError as e:
        console.print(Panel(str(e), border_style="red"))
        return 2

    console.print(_menu_principal_panel())

    while True:
        cmd = Prompt.ask(f"[bold {NEON}]{PROMPT}[/bold {NEON}]").strip()
        cmd_low = cmd.lower()

        if cmd_low in ("exit", "salir", "quit", "q"):
            console.print(Panel("Saliendo...", border_style=NEON))
            return 0

        if cmd_low == "clear":
            console.clear()
            console.print(_title_bar(APP_TITLE))
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "menu":
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "analisis":
            run_analisis(console, loader)
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "estadisticas":
            # data puede recargarse internamente; pero pasamos loader para reload en esa sección
            run_estadisticas(console, loader)
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "dashboards":
            run_dashboards(console)
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "matriz de riesgos":
            run_matriz_riesgos(console)
            console.print(_menu_principal_panel())
            continue

        if cmd_low == "modelo predictivo":
            run_modelo_predictivo(console)
            console.print(_menu_principal_panel())
            continue

        console.print(Panel("Comando no reconocido. Escribe una opción del menú o 'exit'.", border_style="yellow"))
        console.print(_menu_principal_panel())