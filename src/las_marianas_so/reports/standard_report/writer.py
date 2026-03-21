"""
Módulo de Escritura en Word para el Reporte Estándar.
Versión FINAL con aplicación de estilos de tabla segura.
"""
from pathlib import Path
import pandas as pd
from docx import Document
from docx.text.paragraph import Paragraph
from docx.shared import Inches
from docx.table import Table

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

# --- FUNCIÓN DE AYUDA DE ESTILO SEGURO (ADAPTADA DEL CÓDIGO DE REFERENCIA) ---
def _apply_table_style_safely(tbl: Table):
    """
    Intenta aplicar una lista de estilos de tabla comunes y usa el primero que funcione.
    Si ninguno funciona, no detiene el programa.
    """
    # Lista de nombres de estilo comunes en español e inglés
    preferred_styles = [
        "Table Grid", "Grid Table 1 Light", "Light Grid", 
        "Tabla con cuadrícula", "Cuadrícula clara"
    ]
    for style_name in preferred_styles:
        try:
            # El bloque try...except es la clave para que no falle
            tbl.style = style_name
            return # Si tiene éxito, salimos de la función
        except KeyError:
            # Si el estilo no existe, simplemente continuamos con el siguiente
            continue
    # Si después del bucle no se encontró ningún estilo, lo notificamos.
    print(f"[yellow]Advertencia: Ninguno de los estilos de tabla preferidos se encontró. Se usará el estilo por defecto.[/yellow]")


# --- FUNCIÓN UNIFICADA, SIMPLIFICADA Y CORREGIDA ---
def insert_content_at_anchor(doc: Document, anchor_text: str, data: pd.Series, image_path: Path):
    """
    Busca un ancla y la reemplaza con una tabla y un gráfico.
    """
    anchor_paragraph = find_paragraph(doc, anchor_text)
    if not anchor_paragraph:
        print(f"[bold yellow]Advertencia: No se encontró el ancla '{anchor_text}' en la plantilla.[/bold yellow]")
        return
        
    # --- MÉTODO SIMPLE Y DIRECTO ---
    # 1. Elimina el texto del ancla.
    anchor_paragraph.clear()
    
    # 2. Añadir la tabla y aplicar estilo de forma SEGURA.
    table = doc.add_table(rows=1, cols=3)
    _apply_table_style_safely(table) # <--- ¡AQUÍ ESTÁ LA CORRECCIÓN!
    
    # Rellenar la tabla
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text, hdr_cells[1].text, hdr_cells[2].text = 'Categoría', 'Cantidad', 'Porcentaje'
    
    total_items = data.sum()
    for category, count in data.items():
        row_cells = table.add_row().cells
        row_cells[0].text = str(category)
        row_cells[1].text = str(int(count))
        percentage = (count / total_items * 100) if total_items > 0 else 0
        row_cells[2].text = f'{percentage:.1f}%'

    # Mover el párrafo ancla después de la tabla
    table._tbl.addnext(anchor_paragraph._p)

    # 3. Añadir la imagen en el párrafo ancla (que ahora está debajo de la tabla)
    run = anchor_paragraph.add_run()
    run.add_picture(str(image_path), width=Inches(5.5))
    anchor_paragraph.alignment = 1 # Centrar

    # 4. Añadir espacio para el siguiente elemento
    doc.add_paragraph()