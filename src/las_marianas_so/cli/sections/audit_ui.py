"""
Interfaz de Usuario para el Módulo de Auditoría.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import IntPrompt

from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.audit.core import run_audit_on_sheet

def show_audit_menu(console: Console, loader: ExcelLoader):
    """
    Muestra el menú para seleccionar una hoja y ejecutar la auditoría.
    """
    sheet_options = {
        str(i + 1): alias 
        for i, alias in enumerate(loader.get_data().keys())
    }
    
    # Crear el texto del menú dinámicamente
    menu_text = "[bold]Seleccione la hoja que desea auditar:[/bold]\n\n"
    for num, alias in sheet_options.items():
        menu_text += f"{num}. [cyan]{alias.replace('_', ' ').title()}[/cyan]\n"
    
    console.print(Panel(menu_text, title="Módulo de Auditoría", border_style="bold magenta"))

    # Pedir al usuario que elija una opción
    choice = IntPrompt.ask(
        "Ingrese el número de la hoja", 
        choices=list(sheet_options.keys()),
        show_choices=False # Ya mostramos las opciones en el panel
    )
    
    selected_alias = sheet_options[str(choice)]
    selected_df = loader.get_data()[selected_alias]

    console.print(f"\n[bold]Ejecutando auditoría en la hoja '{selected_alias}'...[/bold]")
    
    # Ejecutar la auditoría solo para la hoja seleccionada
    missing_summary = run_audit_on_sheet(selected_df, selected_alias)
    
    # Mostrar los resultados
    display_audit_results(missing_summary, selected_alias)


def display_audit_results(missing_summary: dict, sheet_alias: str):
    """
    Muestra los resultados de la auditoría en la consola en formato de resumen.
    """
    console = Console()

    if not missing_summary:
        console.print(Panel(
            f"[bold green]✅ Auditoría completada en '{sheet_alias}'. No se encontraron valores faltantes.[/bold green]"
        ))
        return

    console.print(Panel(
        f"[bold yellow]⚠️ Se encontraron valores faltantes en la hoja '{sheet_alias}'.[/bold yellow]"
    ))

    # Crear la nueva tabla de resumen
    table = Table(
        show_header=True, 
        header_style="bold blue",
        title=f"Resumen de Valores Faltantes en '{sheet_alias}'"
    )
    table.add_column("Columna", style="cyan", no_wrap=True)
    table.add_column("Cantidad de Registros Faltantes", style="red", justify="right")

    for column, count in missing_summary.items():
        table.add_row(column, str(count))
        
    console.print(table)