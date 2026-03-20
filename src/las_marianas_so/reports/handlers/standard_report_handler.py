"""
Manejador (Handler) para el Reporte Estándar.
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

    # 1. Obtener los trabajadores activos para este contexto
    df_activos = domain.get_active_workers(data, obra, year, month)
    if df_activos.empty:
        console.print(f"[bold red]No se encontraron trabajadores activos para '{obra}' en {month}/{year}. No se puede generar el reporte.[/bold red]")
        return
    
    console.print(f" -> Se encontraron {len(df_activos)} trabajadores activos.")

    # 2. Calcular todas las estadísticas de una vez
    stats = domain.calculate_all_statistics(df_activos)
    console.print(" -> Estadísticas calculadas.")

    # 3. Generar e insertar cada sección (gráfico)
    secciones = {
        "Apartado A": {"anchor": "Epidemiología laboral", "data": stats['apartado_a'], "title": "Gráfico A: Distribución por Sexo"},
        "Apartado B": {"anchor": "Grupos Etarios", "data": stats['apartado_b'], "title": "Gráfico B: Distribución por Edad"},
        "Apartado C": {"anchor": "Status EMO", "data": stats['apartado_c'], "title": "Gráfico C: Estatus de EMO"},
        "Apartado D": {"anchor": "Perfiles EMO", "data": stats['apartado_d'], "title": "Gráfico D: Perfiles de EMO"},
        "Apartado E": {"anchor": "Vigencia EMO", "data": stats['apartado_e'], "title": "Gráfico E: Vigencia de EMO"},
        "Apartado F": {"anchor": "Aptitud EMO", "data": stats['apartado_f'], "title": "Gráfico F: Aptitud de EMO"},
    }

    for key, info in secciones.items():
        console.print(f"   - Procesando {key}...")
        chart_path = temp_dir / f"{key.replace(' ', '_').lower()}.png"
        
        # Crear el gráfico
        charts.create_donut_chart(
            labels=info['data'].index,
            values=info['data'].values,
            title=info['title'],
            out_path=chart_path
        )
        
        # Insertar el gráfico en el Word
        writer.insert_image_after_anchor(doc, info['anchor'], chart_path)
    
    console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")
