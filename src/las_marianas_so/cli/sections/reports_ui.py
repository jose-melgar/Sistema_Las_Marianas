"""
Interfaz de Usuario para el Módulo de Generación de Reportes.
"""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.reports.core import generate_standard_report

def get_unique_obras(loader: ExcelLoader) -> list[str]:
    # ... (sin cambios) ...
    try:
        df_trabajadores = loader.get_data()['trabajadores']
        obras = df_trabajadores['obra'].dropna().unique()
        return sorted([str(obra) for obra in obras])
    except KeyError:
        return []

def show_reports_menu(console: Console, loader: ExcelLoader):
    # ... (toda la recopilación de datos es igual) ...
    console.print(Panel(
        "Asistente de Generación de Reportes",
        title="Módulo de Reportes",
        border_style="bold green"
    ))

    # --- 1. Seleccionar Obra ---
    obras = get_unique_obras(loader)
    if not obras:
        console.print("[bold red]No se pudieron cargar las obras desde la hoja de trabajadores.[/bold red]")
        return
        
    obra_options = {str(i + 1): obra for i, obra in enumerate(obras)}
    menu_text = "[bold]Seleccione la Obra:[/bold]\n\n"
    for num, obra in obra_options.items():
        menu_text += f"{num}. [cyan]{obra}[/cyan]\n"
    console.print(Panel(menu_text))
    obra_choice = IntPrompt.ask("Ingrese el número de la obra", choices=list(obra_options.keys()))
    selected_obra = obra_options[str(obra_choice)]

    # --- 2. Ingresar Año y Mes ---
    current_year = 2024
    selected_year = IntPrompt.ask("Ingrese el año del reporte", default=current_year)
    selected_month = IntPrompt.ask("Ingrese el mes del reporte (1-12)", choices=[str(i) for i in range(1, 13)])
    
    # --- 3. Seleccionar Tipo de Reporte ---
    report_types = {
        '1': "Reporte Estandar",
        '2': "Reporte de Vulnerabilidad"
    }
    menu_text = "[bold]Seleccione el Tipo de Reporte:[/bold]\n\n1. Reporte Estandar\n2. Reporte de Vulnerabilidad"
    console.print(Panel(menu_text))
    report_choice = Prompt.ask("Ingrese el número del tipo de reporte", choices=['1', '2'])
    selected_report_type = report_types[report_choice]
    
    console.print(
        f"\n[bold]Contexto recopilado:[/bold]\n"
        f" - Obra: [yellow]{selected_obra}[/yellow]\n"
        f" - Período: [yellow]{selected_month:02d}/{selected_year}[/yellow]\n"
        f" - Tipo: [yellow]{selected_report_type}[/yellow]"
    )
    
    # --- 4. LLAMADA AL CORE (Ahora pasamos el diccionario de datos) ---
    generate_standard_report(
        data=loader.get_data(), # <--- AÑADIDO
        obra=selected_obra,
        year=selected_year,
        month=selected_month,
        report_type=selected_report_type
    )

    input("\nPresione Enter para volver al menú principal...")
