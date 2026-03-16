"""
Pantalla de inicio profesional con animaciones
"""
import time
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.align import Align


class SplashScreen:
    """Pantalla de inicio animada del sistema"""
    
    def __init__(self):
        self.console = Console()
    
    def mostrar_banner(self):
        """Muestra el banner principal con ASCII art"""
        self.console.clear()
        
        # Crear el banner más compacto
        banner = Text()
        banner.append("╔════════════════════════════════════════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner.append("║                                                                                                    ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("██╗      █████╗ ███████╗    ███╗   ███╗ █████╗ ██████╗ ██╗ █████╗ ███╗   ██╗ █████╗ ██████╗", style="bold green")
        banner.append("    ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("██║     ██╔══██╗██╔════╝    ████╗ ████║██╔══██╗██╔══██╗██║██╔══██╗████╗  ██║██╔══██╗██╔════╝", style="bold green")
        banner.append("   ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("██║     ███████║███████╗    ██╔████╔██║███████║██████╔╝██║███████║██╔██╗ ██║███████║███████╗", style="bold green")
        banner.append("   ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("██║     ██╔══██║╚════██║    ██║╚██╔╝██║██╔══██║██╔══██╗██║██╔══██║██║╚██╗██║██╔══██║╚════██║", style="bold green")
        banner.append("   ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("███████╗██║  ██║███████║    ██║ ╚═╝ ██║██║  ██║██║  ██║██║██║  ██║██║ ╚████║██║  ██║███████║", style="bold green")
        banner.append("   ║\n", style="bold cyan")
        banner.append("║     ", style="bold cyan")
        banner.append("╚══════╝╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝", style="bold green")
        banner.append("   ║\n", style="bold cyan")
        banner.append("║                                                                                                    ║\n", style="bold cyan")
        banner.append("║                          ", style="bold cyan")
        banner.append("          🏥  CONSULTORIO MÉDICO  🏥        ", style="bold yellow")
        banner.append("                              ║\n", style="bold cyan")
        banner.append("║                                                                                                    ║\n", style="bold cyan")
        banner.append("║                      ", style="bold cyan")
        banner.append("          Sistema de Ticketera Térmica v3.0          ", style="bold white")
        banner.append("                         ║\n", style="bold cyan")
        banner.append("║                        ", style="bold cyan")
        banner.append("    [MODO: TERMINAL SEGURA - ACCESO AUTORIZADO]            ", style="bold red")
        banner.append("                 ║\n", style="bold cyan")
        banner.append("║                                                                                                    ║\n", style="bold cyan")
        banner.append("╚════════════════════════════════════════════════════════════════════════════════════════════════════╝", style="bold cyan")

        self.console.print(Align.center(banner))
        self.console.print()
    
    def animacion_carga(self):
        """Muestra animacion de carga del sistema"""
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            # Tarea 1: Inicializando sistema
            task1 = progress.add_task("[cyan]🔐 Inicializando sistema seguro...", total=100)
            for _ in range(100):
                time.sleep(0.008)
                progress.update(task1, advance=1)
            
            # Tarea 2: Verificando directorios
            task2 = progress.add_task("[cyan]📁 Verificando estructura de archivos...", total=100)
            for _ in range(100):
                time.sleep(0.006)
                progress.update(task2, advance=1)
            
            # Tarea 3: Cargando catalogo
            task3 = progress.add_task("[cyan]📋 Cargando catálogo de productos...", total=100)
            for _ in range(100):
                time.sleep(0.007)
                progress.update(task3, advance=1)
            
            # Tarea 4: Inicializando base de datos
            task4 = progress.add_task("[cyan]💾 Conectando con base de datos...", total=100)
            for _ in range(100):
                time.sleep(0.009)
                progress.update(task4, advance=1)
            
            # Tarea 5: Validando permisos
            task5 = progress.add_task("[cyan]🔑 Validando permisos de escritura...", total=100)
            for _ in range(100):
                time.sleep(0.005)
                progress.update(task5, advance=1)
            
            # Tarea 6: Sistema listo
            task6 = progress.add_task("[green]✅ Sistema operativo...", total=100)
            for _ in range(100):
                time.sleep(0.004)
                progress.update(task6, advance=1)
        
        self.console.print()
    
    def mensaje_bienvenida(self):
        """Muestra mensaje de bienvenida"""
        mensaje = Panel(
            "[bold green]Sistema inicializado correctamente[/bold green]\n\n"
            "[cyan]Presione ENTER para continuar...[/cyan]",
            title="[bold yellow]⚡ SISTEMA LISTO ⚡[/bold yellow]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(Align.center(mensaje))
        input()
        self.console.clear()