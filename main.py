"""
Punto de Entrada Principal de la Aplicación.
"""
import sys
from pathlib import Path
from rich.console import Console

# Añadir 'src' al path de Python para que encuentre los módulos
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR / 'src') not in sys.path:
    sys.path.append(str(ROOT_DIR / 'src'))

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.cli.main_console import run_console
from las_marianas_so.cli.splash_screen import show_splash_screen


def main():
    """Función principal que arranca el sistema."""
    console = Console()
    show_splash_screen()

    try:
        console.print("[bold green]Cargando datos desde Excel...[/bold green]")
        loader = ExcelLoader(base_path=ROOT_DIR)
        console.print("[bold green]¡Datos cargados exitosamente![/bold green]\n")

        # Pasamos la raíz del repo para poder levantar dashboard desde CLI
        run_console(loader, repo_root=ROOT_DIR)

    except (ValueError, FileNotFoundError) as e:
        console.print(f"[bold red]Error Crítico al cargar la configuración o el archivo Excel:[/bold red]\n{e}")
        console.print("Asegúrate de que 'config/loader.config.yml' y el archivo Excel referenciado existan.")
    except Exception as e:
        console.print(f"[bold red]Ocurrió un error inesperado al iniciar:[/bold red]\n{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()