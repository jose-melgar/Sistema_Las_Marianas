from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.cli.dashboard_runner import run_dashboard


def show_dashboard_menu(console: Console, loader: ExcelLoader, repo_root: Path):
    """
    Menú simple para levantar dashboard (API + Frontend).
    Nota: `loader` aquí no se usa todavía, pero lo mantenemos para consistencia con el CLI.
    """
    console.print(Panel(
        "[bold]Dashboard[/bold]\n\n"
        "Esto abrirá:\n"
        " - API en http://127.0.0.1:8000\n"
        " - Frontend en http://127.0.0.1:5500/static_dashboard/\n\n"
        "Mientras el dashboard esté abierto, esta consola quedará ocupada.\n",
        title="Módulo Dashboard",
        border_style="bold yellow"
    ))

    open_browser = Prompt.ask("¿Abrir navegador automáticamente?", choices=["s", "n"], default="s") == "s"

    api_port = IntPrompt.ask("Puerto API", default=8000)
    web_port = IntPrompt.ask("Puerto Frontend", default=5500)

    console.print("\n[bold yellow]Iniciando dashboard... (Ctrl+C para detener)[/bold yellow]\n")

    # Ejecuta bloqueante (hasta Ctrl+C)
    run_dashboard(
        repo_root=repo_root,
        api_port=api_port,
        web_port=web_port,
        open_browser=open_browser,
        reload=False,
    )