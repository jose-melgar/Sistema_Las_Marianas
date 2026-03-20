"""
Core del Sistema de Generación de Reportes (Actúa como Router).
"""
from pathlib import Path
from docx import Document
from rich.console import Console

from .handlers import standard_report_handler

console = Console()

def _find_text_in_doc(doc: Document, text_to_find: str) -> bool:
    text_to_find_lower = text_to_find.lower()
    for p in doc.paragraphs:
        if text_to_find_lower in p.text.lower(): return True
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    if text_to_find_lower in p.text.lower(): return True
    return False

# El nombre de la función se mantiene, pero ahora recibe 'data' desde la UI
def generate_standard_report(data: dict, obra: str, year: int, month: int, report_type: str):
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    template_path = base_path / "templates/informes/prueba.docx"
    output_path_dir = base_path / "outputs"
    temp_dir = output_path_dir / "temp_charts" # Carpeta para gráficos temporales
    
    output_path_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    
    if not template_path.exists():
        console.print(f"[bold red]Error: No se encuentra la plantilla en:[/bold red] {template_path}")
        return

    doc = Document(template_path)
    
    if not _find_text_in_doc(doc, report_type):
        console.print(f"[bold red]Error de Plantilla:[/bold red] El archivo no es válido para un '{report_type}'.")
        return
        
    console.print(f"[bold green]Validación de plantilla exitosa.[/bold green]")
    
    # Enrutamiento: decide a qué manejador llamar
    if report_type == "Reporte Estandar":
        # Ahora pasamos todo el contexto necesario al manejador
        standard_report_handler.run(doc, data, obra, year, month, temp_dir)
    
    elif report_type == "Reporte de Vulnerabilidad":
        console.print("[yellow]El 'Reporte de Vulnerabilidad' aún no está implementado.[/yellow]")
    
    # Guardado final
    output_filename = f"Reporte_{obra.replace(' ', '_')}_{year}_{month:02d}.docx"
    output_path = output_path_dir / output_filename
    doc.save(output_path)
    
    console.print(f"\n[bold green]¡Reporte generado![/bold green] Puedes encontrarlo en: [cyan]{output_path}[/cyan]")