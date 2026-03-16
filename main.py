"""
Punto de Entrada Principal (Entry Point) para la aplicación Las Marianas SO.

Este script se encarga de:
1. Parsear los argumentos de la línea de comandos.
2. Inicializar los componentes principales del sistema (Loader, Orquestador).
3. Lanzar el modo de operación solicitado (CLI interactivo).
"""
import argparse
from pathlib import Path

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.reports.orchestrator import ReportOrchestrator
from las_marianas_so.cli.main_console import run_console
from las_marianas_so.cli.splash_screen import show_splash_screen

# La ruta base del proyecto es el directorio donde se encuentra este script.
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUTS_PATH = PROJECT_ROOT / "outputs"

def main():
    """Función principal que orquesta el inicio de la aplicación."""
    parser = argparse.ArgumentParser(description="Sistema de Gestión de SO - Las Marianas")
    parser.add_argument(
        '--cli', 
        action='store_true', 
        help="Ejecuta la aplicación en modo CLI interactivo."
    )
    parser.add_argument(
        '--no-splash',
        action='store_true',
        help="Omite la pantalla de bienvenida."
    )
    args = parser.parse_args()

    if not args.no_splash:
        show_splash_screen()

    if args.cli:
        try:
            # 1. Inicializar el Loader (carga todos los datos)
            loader = ExcelLoader(base_path=PROJECT_ROOT)
            
            # 2. Inicializar el Orquestador de Reportes
            report_orchestrator = ReportOrchestrator(
                loader_data=loader.get_data(), 
                base_output_path=OUTPUTS_PATH
            )
            
            # 3. Lanzar la consola principal
            run_console(loader, report_orchestrator)
            
        except FileNotFoundError as e:
            print(f"\n[ERROR CRÍTICO] No se pudo iniciar la aplicación: {e}")
            print("Asegúrese de que los archivos de configuración y datos existan en las rutas correctas.")
        except Exception as e:
            print(f"\n[ERROR INESPERADO] Ocurrió un problema: {e}")
            
    else:
        print("Modo no especificado. Use --cli para iniciar la consola interactiva.")


if __name__ == "__main__":
    main()