"""
Módulo de Generación de Gráficos para el Reporte Estándar.
Actualizado con estética Cyberpunk/Pastel y nuevos tipos de gráficos.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

CYBERPUNK_COLORS = ["#00F6F6", "#FF00FF", "#F6F600", "#00FF00", "#FF5F1F", "#8A2BE2"]


def _save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)


def _add_gradient_background(ax, colors=("#E0F7FA", "#FFFFFF"), alpha=0.6):
    """Añade fondo degradado suave (hex -> RGB numérico)."""
    c0 = np.array(mcolors.to_rgb(colors[0]), dtype=float)
    c1 = np.array(mcolors.to_rgb(colors[1]), dtype=float)

    # gradiente horizontal: 2 filas x 256 columnas x 3 canales RGB
    t = np.linspace(0.0, 1.0, 256)
    row = (1 - t)[:, None] * c0 + t[:, None] * c1
    grad = np.tile(row[None, :, :], (2, 1, 1))

    ax.imshow(
        grad,
        interpolation="bicubic",
        extent=(0, 1, 0, 1),
        transform=ax.transAxes,
        aspect="auto",
        zorder=-2,
        alpha=alpha
    )


def create_donut_chart(labels, values, title: str, out_path: Path):
    values_int = [int(v) for v in values] if values is not None else []
    total = sum(values_int)

    fig, ax = plt.subplots(figsize=(7.6, 4.6), facecolor='none')
    _add_gradient_background(ax)
    ax.set_title(title, fontsize=14, fontweight="bold", color='#333333')

    if total <= 0:
        labels, values_int = ["Sin datos"], [1]

    palette = CYBERPUNK_COLORS[:len(values_int)] or ["#00F6F6"]
    wedges, _, autotexts = ax.pie(
        values_int,
        labels=None,
        colors=palette,
        startangle=90,
        counterclock=False,
        radius=1.0,
        wedgeprops=dict(width=0.40, edgecolor='white', linewidth=1.5),
        autopct=lambda p: f"{p:.0f}%" if p > 5 else "",
        pctdistance=0.8
    )
    plt.setp(autotexts, size=10, weight="bold", color="black")
    ax.set_aspect("equal")

    legend_labels = ["Sin datos"] if total <= 0 else [
        f"{lab}: {val} ({(val/total)*100:.1f}%)" for lab, val in zip(labels, values_int)
    ]
    ax.legend(
        wedges,
        legend_labels,
        title="Detalle",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False
    )

    fig.subplots_adjust(left=0.06, right=0.70, top=0.88, bottom=0.10)
    _save_fig(fig, out_path)


def create_barh_chart(labels, values, title: str, out_path: Path):
    values_int = [int(v) for v in values] if values is not None else []
    if not values_int:
        values_int = [0] * len(labels)

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='none')
    _add_gradient_background(ax)
    ax.set_title(title, fontsize=14, fontweight="bold", color='#333333')

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values_int, align='center', color=CYBERPUNK_COLORS[0], height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('Cantidad')

    max_v = max(values_int) if values_int else 0
    for bar in bars:
        width = bar.get_width()
        offset = max(max_v * 0.01, 0.2)
        ax.text(width + offset, bar.get_y() + bar.get_height() / 2.0, f"{int(width)}", va='center', ha='left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD')
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

    fig.tight_layout()
    _save_fig(fig, out_path)


def create_triple_donut_aptitud(counts_f, counts_total, counts_m, title: str, out_path: Path):
    """
    Gráfico triple de anillos para Aptitud:
    izquierda = femenino, centro = general, derecha = masculino.
    Cada gráfico tiene su propia leyenda.
    """
    order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]

    def to_series_counts(x):
        if x is None:
            s = pd.Series(dtype="int64")
        elif isinstance(x, pd.Series):
            s = x.copy()
        elif isinstance(x, dict):
            s = pd.Series(x)
        else:
            s = pd.Series(dtype="int64")

        s.index = [str(i).strip().upper() for i in s.index]
        s = pd.to_numeric(s, errors="coerce").fillna(0).astype(int)

        alias_map = {
            "APTO CON RESTRICCIÓN": "CON RESTRICCIONES",
            "APTO CON RESTRICCION": "CON RESTRICCIONES",
            "CON RESTRICCION": "CON RESTRICCIONES",
            "CON RESTRICCIONES": "CON RESTRICCIONES",
            "NO APTO": "NO APTO",
            "OBSERVADO": "OBSERVADO",
            "APTO": "APTO",
        }
        s = s.rename(index=alias_map)
        s = s.groupby(level=0).sum()
        s = s.reindex(order).fillna(0).astype(int)
        return s

    sf = to_series_counts(counts_f)
    st = to_series_counts(counts_total)
    sm = to_series_counts(counts_m)

    color_map = {
        "APTO": "#4C78A8",
        "CON RESTRICCIONES": "#54A24B",
        "NO APTO": "#E45756",
        "OBSERVADO": "#F2CF5B",
    }
    color_list = [color_map[k] for k in order]

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.0), facecolor="none")
    fig.suptitle(title, fontsize=14, fontweight="bold", color="#333333", y=0.98)

    panel_titles = ["APTITUD DE MUJERES", "APTITUD DE TRABAJADORES", "APTITUD DE HOMBRES"]

    for ax in axes:
        _add_gradient_background(ax, alpha=0.45)

    def legend_labels_for(s: pd.Series):
        total = int(s.sum())
        if total <= 0:
            return ["Sin datos"]
        return [f"{k}: {int(s[k])} ({(int(s[k]) / total) * 100:.0f}%)" for k in order]

    def draw_one(ax, s_counts: pd.Series, subtitle: str, legend_side: str):
        vals = s_counts.values.tolist()
        total = int(sum(vals))

        ax.set_title(subtitle, fontsize=10, fontweight="bold", color="#333333", pad=8)

        if total <= 0:
            wedges, _, _ = ax.pie(
                [1],
                labels=None,
                colors=["#C9C9C9"],
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.40, edgecolor="white", linewidth=1.2),
                autopct=lambda p: ""
            )
            labels = ["Sin datos"]
        else:
            wedges, _, autotexts = ax.pie(
                vals,
                labels=None,
                colors=color_list,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.40, edgecolor="white", linewidth=1.2),
                autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
                pctdistance=0.82
            )
            plt.setp(autotexts, size=8, weight="bold", color="black")
            labels = legend_labels_for(s_counts)

        ax.set_aspect("equal")

        if legend_side == "left":
            ax.legend(
                wedges, labels, title="Detalle",
                loc="center right", bbox_to_anchor=(-0.10, 0.5),
                frameon=False, fontsize=8, title_fontsize=9
            )
        elif legend_side == "right":
            ax.legend(
                wedges, labels, title="Detalle",
                loc="center left", bbox_to_anchor=(1.10, 0.5),
                frameon=False, fontsize=8, title_fontsize=9
            )
        else:
            ax.legend(
                wedges, labels, title="Detalle",
                loc="upper center", bbox_to_anchor=(0.5, -0.08),
                ncol=2, frameon=False, fontsize=8, title_fontsize=9
            )

    draw_one(axes[0], sf, panel_titles[0], legend_side="left")
    draw_one(axes[1], st, panel_titles[1], legend_side="center")
    draw_one(axes[2], sm, panel_titles[2], legend_side="right")

    fig.subplots_adjust(left=0.06, right=0.94, top=0.84, bottom=0.18, wspace=0.24)
    _save_fig(fig, out_path)