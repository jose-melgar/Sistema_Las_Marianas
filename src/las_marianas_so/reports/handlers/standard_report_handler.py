"""
Manejador (Handler) para el Reporte Estándar.
Adaptado para el nuevo writer simplificado.
"""
from pathlib import Path
from rich.console import Console

from ..standard_report import domain, charts, writer

console = Console()

def run(doc, data: dict, obra: str, year: int, month: int, temp_dir: Path):
    """
    Función principal que ejecuta todos los pasos para generar el Reporte Estándar.
    """
    console.print("\n[bold]Iniciando manejador del Reporte Estándar...[/bold]")

    df_activos = domain.get_active_workers(data, obra, year, month)
    if df_activos.empty:
        console.print(f"[bold red]No se encontraron trabajadores activos. No se puede generar el reporte.[/bold red]")
        return
    
    console.print(f" -> Se encontraron {len(df_activos)} trabajadores activos.")

    stats = domain.calculate_all_statistics(df_activos)
    console.print(" -> Estadísticas calculadas.")

    secciones = {
        "A": {"anchor": "Epidemiología laboral", "data": stats['apartado_a'], "title": "Gráfico A: Distribución por Sexo"},
        "B": {"anchor": "Grupos Etarios", "data": stats['apartado_b'], "title": "Gráfico B: Distribución por Edad"},
        "C": {"anchor": "Status EMO", "data": stats['apartado_c'], "title": "Gráfico C: Estatus de EMO"},
        "D": {"anchor": "Perfiles EMO", "data": stats['apartado_d'], "title": "Gráfico D: Perfiles de EMO"},
        "E": {"anchor": "Vigencia EMO", "data": stats['apartado_e'], "title": "Gráfico E: Vigencia de EMO"},
        "F": {"anchor": "Aptitud EMO", "data": stats['apartado_f'], "title": "Gráfico F: Aptitud de EMO"},
    }

    for key, info in secciones.items():
        console.print(f"   - Procesando Apartado {key} ('{info['anchor']}')...")
        
        if info['data'].empty:
            console.print(f"     [yellow]Sin datos para Apartado {key}, se omite.[/yellow]")
            continue
            
        chart_path = temp_dir / f"apartado_{key.lower()}.png"
        
        # Crear el gráfico
        charts.create_donut_chart(
            labels=info['data'].index,
            values=info['data'].values,
            title=info['title'],
            out_path=chart_path
        )
        
        # Llamar a la función del writer (que ahora es mucho más simple por dentro)
        writer.insert_content_at_anchor(
            doc=doc,
            anchor_text=info['anchor'],
            data=info['data'],
            image_path=chart_path
        )
    
    console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")