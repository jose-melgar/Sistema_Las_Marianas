"""
Módulo de Generación de Gráficos para el Reporte Estándar.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def _save_fig(fig, path: Path):
    """Guarda una figura de matplotlib en una ruta, creando el directorio si es necesario."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)

def _darken(color, factor: float = 0.7):
    """Oscurece un color dado."""
    r, g, b = mcolors.to_rgb(color)
    return (r * factor, g * factor, b * factor)

def create_donut_chart(labels, values, title: str, out_path: Path):
    """
    Crea un gráfico de dona 3D estilizado.
    """
    values_int = [int(v) for v in values] if values is not None else []
    total = sum(values_int)

    if total <= 0:
        labels, values_int = ["Sin datos"], [1]

    colors = ["#1D4ED8", "#38BDF8", "#EC4899", "#0EA5E9", "#F59E0B", "#8B5CF6"][: len(labels)]
    explode = [0.0] * len(labels)
    
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Efecto 3D
    for i in range(14, 0, -1):
        offset = -i * 0.015
        ax.pie(
            values_int, labels=None, colors=[_darken(c) for c in colors],
            startangle=90, counterclock=False, radius=1.0, center=(0, offset),
            explode=explode, wedgeprops=dict(width=0.38, edgecolor="none")
        )

    # Pie principal
    wedges = ax.pie(
        values_int, labels=None, colors=colors, startangle=90, counterclock=False,
        radius=1.0, center=(0, 0), explode=explode, 
        wedgeprops=dict(width=0.38, edgecolor="white", linewidth=1.2),
        autopct=lambda p: f"{p:.0f}%" if p > 0 else "", pctdistance=0.82,
        textprops=dict(color="white", fontsize=11, fontweight="bold")
    )[0]
    
    ax.set_aspect("equal")
    
    legend_labels = ["Sin datos"] if total <= 0 else [f"{lab}: {val} ({(val/total)*100:.1f}%)" for lab, val in zip(labels, values_int)]
    ax.legend(wedges, legend_labels, title="Detalle", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    
    fig.subplots_adjust(left=0.06, right=0.72, top=0.88, bottom=0.10)
    _save_fig(fig, out_path)
    return out_path