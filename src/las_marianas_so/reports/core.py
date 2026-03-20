"""
Core del sistema de generación de reportes.
"""
from pathlib import Path
from docx import Document

def _find_text_in_doc(doc: Document, text_to_find: str) -> bool:
    """Busca un texto específico dentro de todo el documento Word (sin distinción de mayúsculas)."""
    text_to_find_lower = text_to_find.lower()
    for paragraph in doc.paragraphs:
        if text_to_find_lower in paragraph.text.lower():
            return True
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if text_to_find_lower in paragraph.text.lower():
                        return True
    return False

# --- NOMBRE UNIFICADO: generate_standard_report ---
def generate_standard_report(obra: str, year: int, month: int, report_type: str):
    """
    Genera el Reporte Estándar si la plantilla es válida.
    """
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    template_path = base_path / "templates/informes/prueba.docx"
    output_path_dir = base_path / "outputs"
    
    output_path_dir.mkdir(exist_ok=True)
    
    if not template_path.exists():
        print(f"[bold red]Error: No se encuentra la plantilla en:[/bold red] {template_path}")
        return

    doc = Document(template_path)
    
    trigger_text = "Reporte Estandar"
    if not _find_text_in_doc(doc, trigger_text):
        print(f"[bold red]Error de Plantilla:[/bold red] El archivo '{template_path.name}' no es una plantilla válida para un '{report_type}'.")
        print(f"No se encontró el texto de validación: '[bold cyan]{trigger_text}[/bold cyan]'.")
        return
        
    print(f"[bold green]Validación exitosa:[/bold green] Plantilla correcta encontrada.")
    print("Procediendo a escribir el reporte...")
    
    doc.add_paragraph(f"Obra: {obra}")
    doc.add_paragraph(f"Período: {month:02d}/{year}")
    doc.add_paragraph(f"Tipo de Reporte: {report_type}")
    
    output_filename = f"Reporte_{obra.replace(' ', '_')}_{year}_{month:02d}.docx"
    output_path = output_path_dir / output_filename
    doc.save(output_path)
    
    print(f"\n[bold green]¡Reporte generado![/bold green] Lo puedes encontrar en: [cyan]{output_path}[/cyan]")