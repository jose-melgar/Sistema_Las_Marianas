"""
Manejador (Handler) para el Reporte Estándar.

Orquesta la creación del reporte llamando a los módulos especialistas:
domain, charts y writer.
"""
from rich.console import Console

# Importamos los módulos especialistas
from ..standard_report import domain, charts, writer

console = Console()

def run(doc):
    """
    Función principal que ejecuta todos los pasos para generar el Reporte Estándar.
    """
    console.print("\n[bold]Iniciando manejador del Reporte Estándar...[/bold]")
    console.print("Llamando a los módulos especialistas:")
    
    # 1. Llamar a la lógica de dominio para obtener los datos
    calculated_data = domain.calculate_all_statistics()
    
    # 2. Llamar a la lógica de gráficos para crear las imágenes
    generated_charts = charts.create_all_charts(calculated_data)
    
    # 3. Llamar a la lógica de escritura para insertar todo en el documento
    writer.write_content_to_doc(doc, calculated_data, generated_charts)
    
    console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")
