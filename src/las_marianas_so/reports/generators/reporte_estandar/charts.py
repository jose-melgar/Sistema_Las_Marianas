"""
Generación de gráficos específicos para el Informe EMO Estándar.
Versión completa y fiel adaptada del repositorio 'temporal'.
"""
from pathlib import Path
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

def _save_fig(fig, path: Path):
    """Guarda la figura y cierra el plot para liberar memoria."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)

def _darken(color, factor: float = 0.75):
    r, g, b = mcolors.to_rgb(color)
    return (r * factor, g * factor, b * factor)

def donut_chart(labels, values, title: str, out_path: Path):
    """Crea un gráfico de donut 2D estándar."""
    values_int = [int(v) for v in values] if values is not None else []
    total = sum(values_int)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_title(title, fontweight="bold")

    if total <= 0:
        wedges = ax.pie([1], labels=None, startangle=90, counterclock=False)[0]
        legend_labels = ["Sin datos"]
    else:
        wedges = ax.pie(values_int, labels=None, startangle=90, counterclock=False)[0]
        legend_labels = [f"{lab}: {val} ({(val/total)*100:.1f}%)" for lab, val in zip(labels, values_int)]

    ax.add_artist(plt.Circle((0, 0), 0.60, fc="white"))
    ax.set_aspect("equal")
    ax.legend(wedges, legend_labels, title="Detalle", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    
    fig.subplots_adjust(left=0.06, right=0.72, top=0.88, bottom=0.10)
    _save_fig(fig, out_path)
    return out_path

def donut_3d_stairs(labels, values, title: str, out_path: Path, *, colors=None, startangle: float = 90, thickness: float = 0.38, depth: int = 14, y_step: float = 0.015, explode=None):
    """Crea el característico gráfico de donut 3D con efecto de profundidad."""
    values_int = [int(v) for v in values] if values is not None else []
    total = sum(values_int)

    if total <= 0: labels, values_int = ["Sin datos"], [1]
    if colors is None: colors = ["#1D4ED8", "#EC4899", "#6B7280"][: len(labels)]
    if explode is None: explode = [0.0] * len(labels)

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.set_title(title, fontsize=14, fontweight="bold")

    for i in range(depth, 0, -1):
        ax.pie(values_int, labels=None, colors=[_darken(c, 0.55) for c in colors], startangle=startangle,
               counterclock=False, radius=1.0, center=(0, -i * y_step), explode=explode,
               wedgeprops=dict(width=thickness, edgecolor="none"))

    wedges = ax.pie(values_int, labels=None, colors=colors, startangle=startangle, counterclock=False,
                    radius=1.0, center=(0, 0), explode=explode,
                    wedgeprops=dict(width=thickness, edgecolor="white", linewidth=1.2),
                    autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
                    pctdistance=0.82, textprops=dict(color="white", fontsize=11, fontweight="bold"))[0]
    ax.set_aspect("equal")

    legend_labels = ["Sin datos"] if total <= 0 else [f"{lab}: {val} ({(val/total)*100:.1f}%)" for lab, val in zip(labels, values_int)]
    ax.legend(wedges, legend_labels, title="Detalle", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    
    fig.subplots_adjust(left=0.06, right=0.72, top=0.88, bottom=0.10)
    _save_fig(fig, out_path)
    return out_path

def barh_chart(categories, values, title: str, xlabel: str, out_path: Path):
    """Crea un gráfico de barras horizontales."""
    values_int = [int(v) for v in values] if values is not None else []
    if not list(categories): categories, values_int = ["Sin datos"], [0]
    max_v = max(values_int) if values_int else 0
    pad = max(max_v * 0.1, 1)

    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)

    y = list(range(len(categories)))
    ax.grid(axis="x", color="gray", alpha=0.2, zorder=0)
    for side in ["top", "right"]: ax.spines[side].set_visible(False)

    bars = ax.barh(y, values_int, height=0.6, color="#2F7ED8", zorder=3)
    ax.set_yticks(y, [str(c) for c in categories], fontsize=9)
    ax.set_xlabel(xlabel, fontsize=10, labelpad=8)
    ax.set_xlim(0, max_v + pad)

    for bar in bars:
        w = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        ha, x_pos = ("right", w - pad * 0.05) if w > max_v * 0.15 else ("left", w + pad * 0.05)
        color = "white" if ha == "right" else "black"
        ax.text(x_pos, y_pos, f"{int(w)}", va="center", ha=ha, color=color, fontsize=10, zorder=10, weight="bold")

    ax.invert_yaxis()
    fig.subplots_adjust(left=0.22, right=0.98, top=0.88, bottom=0.15)
    _save_fig(fig, out_path)
    return out_path

def triple_donut_aptitud(counts_f: pd.Series, counts_total: pd.Series, counts_m: pd.Series, out_path: Path):
    """Crea la visualización de tres donuts para el estado de aptitud."""
    order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]
    def norm_counts(s): return s.reindex(order).fillna(0).astype(int)
    cf, ct, cm = norm_counts(counts_f), norm_counts(counts_total), norm_counts(counts_m)

    colors = {"APTO": "#4C78A8", "CON RESTRICCIONES": "#54A24B", "NO APTO": "#E45756", "OBSERVADO": "#F2CF5B"}
    color_list = [colors.get(k, "#CCCCCC") for k in order]

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.0))
    titles = ["APTITUD DE MUJERES", "APTITUD DE TRABAJADORES", "APTITUD DE HOMBRES"]

    def draw_donut(ax, counts, title):
        vals, total = counts.values.tolist(), int(sum(counts.values))
        ax.set_title(title, fontsize=12, fontweight="bold")
        if total <= 0:
            wedges = ax.pie([1], labels=None, colors=["#E0E0E0"], startangle=90)[0]
        else:
            wedges = ax.pie(vals, labels=None, colors=color_list, startangle=90, autopct=lambda p: f"{p:.0f}%" if p > 0 else "", pctdistance=0.85, textprops={'color':"w", 'weight':'bold'})[0]
        ax.add_artist(plt.Circle((0, 0), 0.62, fc="white"))
        ax.set_aspect("equal")
    
    for ax, counts, title in zip(axes, [cf, ct, cm], titles):
        draw_donut(ax, counts, title)
    
    fig.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1, wspace=0.3)
    _save_fig(fig, out_path)
    return out_path