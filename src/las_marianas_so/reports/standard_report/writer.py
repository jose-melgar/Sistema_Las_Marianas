"""
Módulo de Escritura en Word para el Reporte Estándar.
(Placeholder para prueba de conectividad)
"""
from rich.console import Console

console = Console()

def write_content_to_doc(doc, data, charts):
    """Prueba de conectividad para la escritura en el documento."""
    console.print(" -> [purple]Hola, soy writer.py[/purple]")
    # En el futuro, esta función modificaría el objeto 'doc' que recibe.
    doc.add_paragraph("Contenido insertado por writer.py")
