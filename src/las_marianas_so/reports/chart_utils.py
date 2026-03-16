"""
Utilidades para la Generación de Gráficos con Matplotlib.

Adaptado del proyecto `temporal/reportes_estandar`, este módulo provee
funciones estandarizadas para crear los gráficos requeridos por los informes,
como donuts, barras horizontales y agrupaciones de donuts.
"""
import matplotlib.pyplot as plt
from pathlib import Path

# Configuración de estilo global para los gráficos
plt.style.use('seaborn-v0_8-whitegrid')
FONT_COLOR = '#333'
plt.rcParams.update({
    'text.color': FONT_COLOR,
    'axes.labelcolor': FONT_COLOR,
    'xtick.color': FONT_COLOR,
    'ytick.color': FONT_COLOR,
})

def save_chart(fig, output_path: Path, filename: str):
    """Guarda una figura de matplotlib en la ruta especificada."""
    output_path.mkdir(parents=True, exist_ok=True)
    filepath = output_path / filename
    fig.savefig(filepath, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)
    print(f"   -> Gráfico guardado en: {filepath}")

def create_donut_chart(data: pd.Series, title: str, output_path: Path, filename: str):
    """Crea y guarda un gráfico de donut."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    wedges, texts, autotexts = ax.pie(
        data, 
        autopct='%1.1f%%', 
        startangle=90, 
        pctdistance=0.85,
        colors=plt.cm.Pastel1.colors
    )
    
    # Dibujar círculo blanco en el centro para el efecto donut
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax.set_title(title.upper(), weight='bold', size=12, pad=20)
    ax.legend(wedges, data.index, title="Categorías", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    save_chart(fig, output_path, filename)

def create_barh_chart(data: pd.Series, title: str, xlabel: str, output_path: Path, filename: str):
    """Crea y guarda un gráfico de barras horizontales."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    bars = ax.barh(data.index, data.values, color=plt.cm.Pastel2.colors)
    ax.set_title(title.upper(), weight='bold', size=12, pad=20)
    ax.set_xlabel(xlabel)
    
    # Añadir etiquetas de valor en las barras
    for bar in bars:
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(bar.get_width())}', va='center', ha='left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    save_chart(fig, output_path, filename)