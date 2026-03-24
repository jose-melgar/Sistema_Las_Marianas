"""
Router Principal del CLI.

Este módulo contiene el bucle principal de la aplicación de consola.
"""
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.cli.sections.audit_ui import show_audit_menu
from las_marianas_so.cli.sections.reports_ui import show_reports_menu
from las_marianas_so.cli.sections.dashboard_ui import show_dashboard_menu


def run_console(loader: ExcelLoader, *, repo_root: Path):
    """Inicia el bucle principal del menú interactivo del CLI."""
    console = Console()

    while True:
        console.print(Panel(
            "[bold]Menú Principal[/bold]\n\n"
            "1. [cyan]Auditoría de Datos[/cyan]\n"
            "2. [green]Generar Reportes[/green]\n"
            "3. [yellow]Dashboard[/yellow]\n"
            "4. [blue]Matriz de Riesgos (próximamente)[/blue]\n"
            "5. [magenta]Modelo Predictivo (próximamente)[/magenta]\n\n"
            "s. [red]Salir[/red]",
            title="LAS MARIANAS SO",
            border_style="bold blue"
        ))

        choice = Prompt.ask("Seleccione una opción", choices=["1", "2", "3", "4", "5", "s"], default="s")

        if choice == '1':
            show_audit_menu(console, loader)

        elif choice == '2':
            show_reports_menu(console, loader)

        elif choice == '3':
            show_dashboard_menu(console, loader, repo_root)

        elif choice in ['4', '5']:
            console.print("\n[yellow]Este módulo aún no está implementado.[/yellow]\n")

        elif choice == 's':
            console.print("\n[bold]Saliendo del sistema. ¡Hasta luego![/bold]\n")
            break

        console.print("\n" + "=" * 50 + "\n")