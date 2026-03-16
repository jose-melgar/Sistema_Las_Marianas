"""
Interfaz de Usuario para el Módulo de Auditoría.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from las_marianas_so.common.formatting import format_cell

def display_audit_results(audit_results: dict):
    """Muestra los resultados de la auditoría en la consola."""
    console = Console()
    if not audit_results:
        console.print(Panel("[bold green]✅ Auditoría completada. No se encontraron problemas de duplicados o faltantes.[/bold green]"))
        return

    console.print(Panel("[bold yellow]⚠️ Se encontraron problemas en la auditoría de datos. Revise los detalles a continuación.[/bold yellow]"))

    for sheet_alias, issues in audit_results.items():
        console.print(f"\n[bold magenta]Resultados para la hoja '{sheet_alias}':[/bold magenta]")

        # Mostrar Duplicados
        if not issues['duplicates'].empty:
            console.print("\n[yellow]Registros Duplicados Encontrados:[/yellow]")
            df_dupes = issues['duplicates']
            
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Fila Excel", style="dim")
            for col in df_dupes.columns:
                table.add_column(col)
            
            # +2 para la fila de header del excel y el 1-based index
            header_offset = issues.get('header_row', 0) + 2

            for index, row in df_dupes.iterrows():
                row_values = [str(index + header_offset)]
                for col_name in df_dupes.columns:
                    row_values.append(format_cell(row[col_name], col_name))
                table.add_row(*row_values)
            console.print(table)

        # Mostrar Faltantes
        if issues['missing']:
            console.print("\n[yellow]Valores Faltantes Encontrados:[/yellow]")
            header_offset = issues.get('header_row', 0) + 2
            for col, indices in issues['missing'].items():
                filas = ", ".join(str(i + header_offset) for i in indices)
                console.print(f"  - Columna [bold cyan]'{col}'[/bold cyan]: {len(indices)} valores faltantes en filas: [red]{filas}[/red]")
