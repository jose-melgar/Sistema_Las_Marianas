"""
Sección Estadísticas (modo INFORME).

Flujo:
1) Seleccionar Obra desde lista única (Trabajadores.Planta -> obra)
2) Ingresar Año (num)
3) Ingresar Mes (1-12)
4) Elegir apartado del informe (A-F)
5) Mostrar tabla + resumen y generar gráficos como imágenes en /assets/reports

Requisitos:
- Trabajador Activo: Historial_Trabajadores.FechaSalida es nula o posterior al periodo consultado.
- Cruces por DNI normalizado.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table

from utils.loader import ExcelLoader
from utils.formatting import format_cell

NEON = "bright_green"
REPORTS_DIR = Path("assets") / "reports"

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


@dataclass(frozen=True)
class FiltrosInforme:
    obra: str
    anio: int
    mes: int

    @property
    def mes_nombre(self) -> str:
        return MESES.get(self.mes, str(self.mes))


def _ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _period_end(anio: int, mes: int) -> pd.Timestamp:
    """Fecha de corte: fin de mes consultado."""
    # Period('YYYY-MM') -> end_time
    return pd.Period(f"{anio}-{mes:02d}").end_time.normalize()


def _select_obra(console: Console, obras: list[str]) -> str:
    t = Table(title="Seleccione Obra (Planta)", header_style=f"bold {NEON}")
    t.add_column("N°", style=NEON, width=6)
    t.add_column("Obra", style=NEON)
    for i, o in enumerate(obras, start=1):
        t.add_row(str(i), o)
    console.print(t)

    while True:
        choice = Prompt.ask("[cyan]Escriba el número de la obra (o 'menu')[/cyan]").strip().lower()
        if choice == "menu":
            return "menu"
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(obras):
                return obras[idx - 1]
        console.print(Panel("Selección inválida.", border_style="yellow"))


def _ask_filtros_informe(console: Console, loader: ExcelLoader) -> Optional[FiltrosInforme]:
    data = loader.load()

    obras = (
        data.trabajadores["obra"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    obras = sorted([o for o in obras if o])

    if not obras:
        console.print(Panel("No se encontraron obras en Trabajadores.Planta.", border_style="red"))
        return None

    obra = _select_obra(console, obras)
    if obra == "menu":
        return None

    anio = IntPrompt.ask("[cyan]Año (ej: 2026)[/cyan]")
    mes = IntPrompt.ask("[cyan]Mes (1-12)[/cyan]")

    if mes < 1 or mes > 12:
        console.print(Panel("Mes inválido. Debe ser 1 a 12.", border_style="yellow"))
        return None

    return FiltrosInforme(obra=obra, anio=int(anio), mes=int(mes))


def _activos_por_historial(df_hist: pd.DataFrame, obra: str, anio: int, mes: int) -> pd.DataFrame:
    """
    Retorna historial filtrado a activos en obra para el periodo.
    Activo si:
    - obra coincide
    - fecha_ingreso <= fin_periodo (implícito; si hay null ingreso, queda fuera)
    - fecha_salida es NA o fecha_salida > fin_periodo
    """
    corte = _period_end(anio, mes)

    h = df_hist.copy()
    h = h[h["obra"].astype(str).str.strip() == obra.strip()]

    fi = pd.to_datetime(h["fecha_ingreso"], errors="coerce")
    fs = pd.to_datetime(h["fecha_salida"], errors="coerce")

    ingreso_ok = fi.notna() & (fi <= corte)
    salida_ok = fs.isna() | (fs > corte)

    return h.loc[ingreso_ok & salida_ok].copy()


def _trabajadores_activos(df_trab: pd.DataFrame, df_hist: pd.DataFrame, filtros: FiltrosInforme) -> pd.DataFrame:
    activos_hist = _activos_por_historial(df_hist, filtros.obra, filtros.anio, filtros.mes)

    # Cruzar por DNI
    activos_dni = activos_hist[["dni"]].dropna().drop_duplicates()

    t = df_trab.merge(activos_dni, on="dni", how="inner", validate="m:1")
    # ya incluye obra (Planta), sexo, edad, perfil, vigencia, aptitud
    return t


def _table_from_df(console: Console, df: pd.DataFrame, title: str) -> None:
    t = Table(title=title, header_style=f"bold {NEON}")
    for col in df.columns:
        t.add_column(str(col), style=NEON, overflow="fold")
    for _, row in df.iterrows():
        t.add_row(*[format_cell(row[c], str(c)) for c in df.columns])
    console.print(t)


def _save_donut(labels, values, title: str, filename: str) -> Path:
    """
    Donut chart con porcentajes centrados en el grosor del anillo (no pegados al borde).
    """
    _ensure_reports_dir()
    path = REPORTS_DIR / filename

    # Config donut
    width = 0.4
    r_text = 1 - width / 2  # centro del grosor del anillo

    fig, ax = plt.subplots(figsize=(6, 6), dpi=140)

    wedges, _ = ax.pie(
        values,
        labels=labels,
        startangle=90,
        wedgeprops=dict(width=width),
    )

    total = sum(values) if sum(values) else 1

    # Colocar % manualmente en el centro del anillo
    for w, v in zip(wedges, values):
        if v == 0:
            # Si quieres que también se muestre 0.0%, quita este if
            continue

        ang = (w.theta2 + w.theta1) / 2.0
        import math
        x = r_text * math.cos(math.radians(ang))
        y = r_text * math.sin(math.radians(ang))

        pct = (v / total) * 100
        ax.text(
            x,
            y,
            f"{pct:.1f}%",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",  # se lee mejor sobre colores
        )

    ax.set_title(title)
    ax.axis("equal")

    plt.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def _save_barh(labels, series_by_name: dict[str, list[int]], title: str, filename: str) -> Path:
    """
    Barra horizontal (no 3D real; matplotlib 3D complica y rara vez aporta).
    series_by_name: {"Hombres":[...], "Mujeres":[...]}
    """
    _ensure_reports_dir()
    path = REPORTS_DIR / filename

    import numpy as np

    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)
    y = np.arange(len(labels))
    height = 0.35

    keys = list(series_by_name.keys())
    if len(keys) == 1:
        ax.barh(y, series_by_name[keys[0]], height=0.6, label=keys[0])
    else:
        ax.barh(y - height / 2, series_by_name[keys[0]], height=height, label=keys[0])
        ax.barh(y + height / 2, series_by_name[keys[1]], height=height, label=keys[1])

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


# -------------------- Apartados del Informe --------------------

def informe_epidemiologia(console: Console, t_activos: pd.DataFrame, filtros: FiltrosInforme) -> None:
    df = t_activos.copy()

    # Normalizar Sexo a M/F
    df["sexo"] = df["sexo"].astype(str).str.upper().str.strip()
    df.loc[~df["sexo"].isin(["M", "F"]), "sexo"] = "N/D"

    total = len(df)
    if total == 0:
        console.print(Panel("Sin trabajadores activos para el periodo.", border_style="yellow"))
        return

    grp = df.groupby("sexo", dropna=False).agg(
        Cantidad=("dni", "count"),
        EdadProm=("edad", "mean"),
    ).reset_index()

    grp["Porcentaje"] = (grp["Cantidad"] / total * 100).round(1)
    grp["EdadProm"] = grp["EdadProm"].fillna(0).round(1)

    out = grp.rename(columns={"sexo": "Sexo"})[["Sexo", "Cantidad", "Porcentaje", "EdadProm"]]
    _table_from_df(console, out, f"Epidemiología Laboral :: {filtros.obra} :: {filtros.mes_nombre} {filtros.anio}")

    # Donut
    labels = out["Sexo"].tolist()
    values = out["Cantidad"].tolist()
    img = _save_donut(labels, values, "Distribución por Sexo", "A_epidemiologia_sexo.png")
    console.print(Panel(f"Gráfico generado: {img}", border_style=NEON))

    # Resumen inteligente
    edad_m = out.loc[out["Sexo"] == "M", "EdadProm"]
    edad_f = out.loc[out["Sexo"] == "F", "EdadProm"]
    edad_m_val = float(edad_m.iloc[0]) if not edad_m.empty else 0
    edad_f_val = float(edad_f.iloc[0]) if not edad_f.empty else 0

    resumen = f"La edad promedio es de {edad_m_val} años en el sexo masculino y {edad_f_val} en el personal femenino."
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))


def informe_grupo_etario(console: Console, t_activos: pd.DataFrame, filtros: FiltrosInforme) -> None:
    df = t_activos.copy()
    df["sexo"] = df["sexo"].astype(str).str.upper().str.strip()
    df.loc[~df["sexo"].isin(["M", "F"]), "sexo"] = "N/D"

    # bins
    bins = [-float("inf"), 19, 29, 39, 49, 59, float("inf")]
    labels = ["<20", "20-29", "30-39", "40-49", "50-59", ">=60"]
    df["GrupoEtario"] = pd.cut(df["edad"], bins=bins, labels=labels)

    pivot = (
        df.pivot_table(index="GrupoEtario", columns="sexo", values="dni", aggfunc="count", fill_value=0)
        .reset_index()
    )

    # Asegurar columnas M y F
    if "M" not in pivot.columns:
        pivot["M"] = 0
    if "F" not in pivot.columns:
        pivot["F"] = 0

    out = pivot[["GrupoEtario", "M", "F"]].rename(columns={"M": "Hombres", "F": "Mujeres"})
    _table_from_df(console, out, f"Cantidad de Trabajadores según Edad :: {filtros.obra}")

    img = _save_barh(
        labels=out["GrupoEtario"].astype(str).tolist(),
        series_by_name={"Hombres": out["Hombres"].astype(int).tolist(), "Mujeres": out["Mujeres"].astype(int).tolist()},
        title="Trabajadores por Grupo Etario y Sexo",
        filename="B_grupo_etario.png",
    )
    console.print(Panel(f"Gráfico generado: {img}", border_style=NEON))

    # Resumen inteligente
    n_20_29 = int(out.loc[out["GrupoEtario"] == "20-29", ["Hombres", "Mujeres"]].sum(axis=1).iloc[0]) if (out["GrupoEtario"] == "20-29").any() else 0
    n_60 = int(out.loc[out["GrupoEtario"] == ">=60", ["Hombres", "Mujeres"]].sum(axis=1).iloc[0]) if (out["GrupoEtario"] == ">=60").any() else 0
    resumen = f"Existe {n_20_29} trabajadores entre 20-29 años y {n_60} trabajadores mayores de 60."
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))


def informe_estatus_emos(console: Console, registro_emo: pd.DataFrame) -> None:
    df = registro_emo.copy()
    if df.empty:
        console.print(Panel("Registro EMO vacío.", border_style="yellow"))
        return

    # Tomar por NOMBRE el registro con fecha_emo más reciente
    df["fecha_emo"] = pd.to_datetime(df["fecha_emo"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["nombre"])
    df = df.sort_values(by=["nombre", "fecha_emo"], ascending=[True, False])
    df_latest = df.drop_duplicates(subset=["nombre"], keep="first")

    total = len(df_latest)
    entregados = int(df_latest["fecha_entrega"].notna().sum())
    pendientes = int(total - entregados)

    labels = ["Interpretación recibida", "Pendientes"]
    values = [entregados, pendientes]
    img = _save_donut(labels, values, "Estatus de EMO", "C_estatus_emo.png")

    resumen = f"{total} trabajadores presentan exámenes médicos, {entregados} recibieron interpretación y {pendientes} están pendientes."
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))
    console.print(Panel(f"Gráfico generado: {img}", border_style=NEON))


def informe_perfiles_emo(console: Console, t_activos: pd.DataFrame, filtros: FiltrosInforme) -> None:
    df = t_activos.copy()
    df["sexo"] = df["sexo"].astype(str).str.upper().str.strip()
    df.loc[~df["sexo"].isin(["M", "F"]), "sexo"] = "N/D"

    # Map perfil
    perfil = df["perfil"].astype(str).str.strip().str.lower()
    df.loc[perfil == "oficina", "perfil"] = "Administrativo"
    df.loc[perfil == "técnico", "perfil"] = "Operativo"
    df.loc[perfil == "tecnico", "perfil"] = "Operativo"

    pivot = df.pivot_table(index="perfil", columns="sexo", values="dni", aggfunc="count", fill_value=0).reset_index()
    if "M" not in pivot.columns:
        pivot["M"] = 0
    if "F" not in pivot.columns:
        pivot["F"] = 0

    out = pivot[["perfil", "M", "F"]].rename(columns={"perfil": "Perfil", "M": "Hombres", "F": "Mujeres"})
    _table_from_df(console, out, f"Perfiles de EMO (Activos) :: {filtros.obra}")

    n_oper = int(out.loc[out["Perfil"] == "Operativo", ["Hombres", "Mujeres"]].sum(axis=1).iloc[0]) if (out["Perfil"] == "Operativo").any() else 0
    n_adm = int(out.loc[out["Perfil"] == "Administrativo", ["Hombres", "Mujeres"]].sum(axis=1).iloc[0]) if (out["Perfil"] == "Administrativo").any() else 0

    resumen = f"La tabla muestra {n_oper} puestos operativos y {n_adm} administrativos."
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))


def informe_vigencia_emos(console: Console, t_activos: pd.DataFrame, filtros: FiltrosInforme) -> None:
    df = t_activos.copy()
    vig = df["vigencia"].astype("string").str.strip()

    def norm_v(x):
        if x is None or str(x) in ("<NA>", "nan", "None", ""):
            return "Sin EMO"
        x2 = str(x).strip()
        if x2.lower() == "vigente":
            return "Vigente"
        if x2.lower() == "vencido":
            return "Vencido"
        return x2

    df["VigenciaNorm"] = vig.map(norm_v)

    counts = df["VigenciaNorm"].value_counts().reindex(["Vigente", "Vencido", "Sin EMO"], fill_value=0)
    out = pd.DataFrame({"Vigencia": counts.index, "Cantidad": counts.values})
    _table_from_df(console, out, f"Vigencia de EMOS :: {filtros.obra}")

    img = _save_barh(
        labels=out["Vigencia"].tolist(),
        series_by_name={"Total": out["Cantidad"].astype(int).tolist()},
        title="Vigencia de EMOS",
        filename="E_vigencia_emo.png",
    )
    console.print(Panel(f"Gráfico generado: {img}", border_style=NEON))

    resumen = f"El gráfico muestra que {int(counts['Vigente'])} trabajadores tienen EMO vigente, {int(counts['Vencido'])} vencido y {int(counts['Sin EMO'])} están sin EMO."
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))


def informe_aptitud(console: Console, t_activos: pd.DataFrame, filtros: FiltrosInforme) -> None:
    df = t_activos.copy()
    df["sexo"] = df["sexo"].astype(str).str.upper().str.strip()
    df.loc[~df["sexo"].isin(["M", "F"]), "sexo"] = "N/D"

    def norm_a(x):
        if x is None or str(x) in ("<NA>", "nan", "None", ""):
            return "Sin dato"
        x2 = str(x).strip().lower()
        if "apto con" in x2 or "restric" in x2:
            return "Apto con Restricción"
        if x2 == "apto":
            return "Apto"
        if "no apto" in x2:
            return "No Apto"
        if "observ" in x2:
            return "Observado"
        return str(x).strip()

    df["AptitudNorm"] = df["aptitud"].map(norm_a)

    order = ["Apto", "Apto con Restricción", "No Apto", "Observado", "Sin dato"]

    def donut_for(sub: pd.DataFrame, title: str, filename: str) -> Path:
        counts = sub["AptitudNorm"].value_counts().reindex(order, fill_value=0)
        labels = counts.index.tolist()
        values = counts.values.tolist()
        return _save_donut(labels, values, title, filename)

    # Total / Mujeres / Hombres
    img_total = donut_for(df, "Aptitud Médica (Total)", "F_aptitud_total.png")
    img_f = donut_for(df[df["sexo"] == "F"], "Aptitud Médica (Mujeres)", "F_aptitud_mujeres.png")
    img_m = donut_for(df[df["sexo"] == "M"], "Aptitud Médica (Hombres)", "F_aptitud_hombres.png")

    console.print(Panel(f"Gráficos generados:\n- {img_f}\n- {img_total}\n- {img_m}", border_style=NEON))

    counts_total = df["AptitudNorm"].value_counts().reindex(order, fill_value=0)
    total = int(counts_total.sum()) if int(counts_total.sum()) > 0 else 1

    pct_apto = round(int(counts_total["Apto"]) / total * 100, 1)
    pct_restr = round(int(counts_total["Apto con Restricción"]) / total * 100, 1)

    resumen = (
        f"{pct_apto}% se encuentran APTOS, {pct_restr}% APTOS CON RESTRICCIONES, "
        f"{int(counts_total['No Apto'])} NO APTO y {int(counts_total['Observado'])} OBSERVADO."
    )
    console.print(Panel(resumen, border_style=NEON, title="Resumen"))


def run_estadisticas(console: Console, loader: ExcelLoader) -> None:
    console.print(Panel("[bold bright_green]ESTADÍSTICAS (INFORMES)[/bold bright_green]", border_style=NEON))

    filtros = _ask_filtros_informe(console, loader)
    if filtros is None:
        return

    data = loader.load()
    t_activos = _trabajadores_activos(data.trabajadores, data.historial_trabajadores, filtros)

    menu = Table(title="Apartados del Informe", header_style=f"bold {NEON}")
    menu.add_column("Clave", style=NEON, width=6)
    menu.add_column("Apartado", style=NEON)
    menu.add_row("A", "Epidemiología Laboral (Sexo / % / Edad prom) + Anillo")
    menu.add_row("B", "Cantidad de Trabajadores según Edad + Barras")
    menu.add_row("C", "Estatus de EMOS (Registro EMO) + Anillo")
    menu.add_row("D", "Perfiles de EMO (Administrativo/Operativo) Tabla")
    menu.add_row("E", "Vigencia de EMOS (Vigente/Vencido/Sin EMO) + Barras")
    menu.add_row("F", "EMOS según Aptitud Médica + 3 anillos")
    console.print(menu)

    while True:
        choice = Prompt.ask("[cyan]Seleccione apartado (A-F) o 'menu'[/cyan]").strip().upper()
        if choice == "MENU":
            return

        if choice == "A":
            informe_epidemiologia(console, t_activos, filtros)
        elif choice == "B":
            informe_grupo_etario(console, t_activos, filtros)
        elif choice == "C":
            informe_estatus_emos(console, data.registro_emo)
        elif choice == "D":
            informe_perfiles_emo(console, t_activos, filtros)
        elif choice == "E":
            informe_vigencia_emos(console, t_activos, filtros)
        elif choice == "F":
            informe_aptitud(console, t_activos, filtros)
        else:
            console.print(Panel("Opción inválida.", border_style="yellow"))
            continue

        again = Prompt.ask("[cyan]¿Otro apartado? (si/no)[/cyan]").strip().lower()
        if again not in ("si", "s", "yes", "y"):
            return