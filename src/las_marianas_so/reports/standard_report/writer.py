"""
Módulo de Escritura en Word para el Reporte Estándar.
"""
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.shared import Inches

def find_paragraph(doc: Document, text_to_find: str) -> Paragraph | None:
    """Encuentra el primer párrafo que contiene un texto específico."""
    text_to_find_lower = text_to_find.lower()
    for p in doc.paragraphs:
        if text_to_find_lower in p.text.lower():
            return p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if text_to_find_lower in p.text.lower():
                        return p
    return None

def insert_image_after_anchor(doc: Document, anchor_text: str, image_path: Path):
    """Encuentra un texto ancla e inserta una imagen después."""
    anchor_paragraph = find_paragraph(doc, anchor_text)
    if not anchor_paragraph:
        print(f"[bold yellow]Advertencia: No se encontró el ancla '{anchor_text}' en la plantilla.[/bold yellow]")
        return
    
    # Inserta la imagen en un nuevo párrafo después del ancla
    p = anchor_paragraph.insert_paragraph_before() # Insertamos antes para que visualmente quede "después"
    p.alignment = 1 # WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Inches(6.0))
    p.insert_paragraph_before() # Añade un espacio
