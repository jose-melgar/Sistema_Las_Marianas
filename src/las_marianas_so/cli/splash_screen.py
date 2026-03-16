"""
Pantalla de Bienvenida (Splash Screen) para el CLI.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def show_splash_screen():
    """Muestra una pantalla de bienvenida estilizada."""
    console = Console()
    console.print("\n" * 2)
    
    title = Text("Sistema de Gestión de SO - Las Marianas", justify="center", style="bold cyan")
    subtitle = Text("v2.0 - Reestructurado", justify="center", style="italic green")
    
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="bold blue",
        padding=(1, 4)
    )
    
    console.print(panel, justify="center")
    console.print("\n" * 2)