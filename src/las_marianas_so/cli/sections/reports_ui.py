"""
Interfaz de Usuario para el Módulo de Reportes.
"""
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from las_marianas_so.reports.orchestrator import ReportOrchestrator
from las_marianas_so.loader.core import ExcelLoader

def show_reports_menu(console: Console, orchestrator: ReportOrchestrator, loader: ExcelLoader):
    """Muestra el menú para seleccionar y generar reportes."""
    available_reports = orchestrator.list_available_reports()
    if not available_reports:
        console.print("[bold red]No hay reportes configurados.[/bold red]")
        return

    table = Table(title="Reportes Disponibles", show_header=True, header_style="bold green")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre del Reporte")
    table.add_column("Descripción")

    for report_id, config in available_reports.items():
        table.add_row(report_id, config['display_name'], config['description'])
    
    console.print(table)
    
    report_id = Prompt.ask("Ingrese el ID del reporte que desea generar", choices=list(available_reports.keys()))
    
    report_config = available_reports[report_id]
    params = {}
    
    # Recolectar parámetros dinámicamente
    for param_info in report_config.get('parameters', []):
        param_name = param_info['name']
        prompt_text = param_info['prompt']
        
        # Lógica para obtener opciones dinámicas (ej: lista de obras)
        if 'dynamic_options' in param_info:
            options_config = param_info['dynamic_options']
            df_source_alias = options_config['source']
            column = options_config['column']
            
            df = loader.data.get(df_source_alias)
            if df is not None and column in df.columns:
                options = sorted(df[column].unique().tolist())
                params[param_name] = Prompt.ask(prompt_text, choices=options)
            else:
                console.print(f"[red]Error: No se pudieron cargar las opciones para '{param_name}'[/red]")
                return
        elif param_info['type'] == 'int':
            params[param_name] = IntPrompt.ask(prompt_text)
        else: # asume 'str'
            params[param_name] = Prompt.ask(prompt_text)

    orchestrator.run_report(report_id, params)