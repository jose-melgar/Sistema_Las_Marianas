"""
Manejador (Handler) para el Reporte Estándar.
Orquesta la creación de tablas, gráficos y textos de resumen.
"""
from pathlib import Path
from rich.console import Console
import pandas as pd

from ..standard_report import domain, charts, writer

console = Console()


def run(doc, data: dict, obra: str, year: int, month: int, temp_dir: Path):
    console.print("\n[bold]Iniciando manejador del Reporte Estándar...[/bold]")

    df_activos = domain.get_active_workers(data, obra, year, month)
    if df_activos.empty:
        console.print("[red]No se encontraron trabajadores activos. No se puede generar.[/red]")
        return
    console.print(f" -> Se encontraron {len(df_activos)} trabajadores activos.")

    stats = domain.calculate_all_statistics(df_activos, data["trabajadores"], year, month)
    console.print(" -> Estadísticas calculadas.")

    # --- A) Epidemiología laboral ---
    console.print("   - Procesando Apartado A ('Epidemiología laboral')...")
    data_a = stats["apartado_a"]
    chart_path_a = temp_dir / "apartado_a.png"
    charts.create_donut_chart(
        labels=data_a.index,
        values=data_a["Cantidad"],
        title="Gráfico A: Distribución por Sexo",
        out_path=chart_path_a,
    )
    writer.insert_content_at_anchor(
        doc,
        "Epidemiología laboral",
        data_a,
        chart_path_a,
        domain.generate_text_A(data_a),
    )

    # --- B) Grupos Etarios ---
    console.print("   - Procesando Apartado B ('Grupos Etarios')...")
    data_b = stats["apartado_b"]
    chart_path_b = temp_dir / "apartado_b.png"
    charts.create_barh_chart(
        labels=data_b.index,
        values=data_b.values,
        title="Gráfico B: Grupo Etario",
        out_path=chart_path_b,
    )
    writer.insert_content_at_anchor(
        doc,
        "Grupos Etarios",
        data_b,
        chart_path_b,
        domain.generate_text_B(data_b),
    )

    # --- C) Status EMO (C1 + C2 en la misma ancla) ---
    console.print("   - Procesando Apartado C ('Status EMO')...")

    data_c1 = stats["apartado_c1"]
    chart_path_c1 = temp_dir / "apartado_c1.png"
    charts.create_donut_chart(
        labels=data_c1.index,
        values=data_c1.values,
        title="Gráfico C1: Cobertura General de EMOs",
        out_path=chart_path_c1,
    )

    data_c2 = stats["apartado_c2"]
    chart_path_c2 = temp_dir / "apartado_c2.png"
    charts.create_donut_chart(
        labels=data_c2.index,
        values=data_c2.values,
        title="Gráfico C2: Entrega de EMOs del Mes",
        out_path=chart_path_c2,
    )

    writer.insert_multiple_contents_at_anchor(
        doc,
        "Status EMO",
        items=[
            {"data": data_c1, "image_path": chart_path_c1, "summary_text": domain.generate_text_C1(data_c1)},
            {"data": data_c2, "image_path": chart_path_c2, "summary_text": domain.generate_text_C2(data_c2)},
        ],
        remove_anchor=True,
    )

    # --- D) Perfiles EMO ---
    if "apartado_d" in stats:
        console.print("   - Procesando Apartado D ('Perfiles EMO')...")
        data_d = stats["apartado_d"]
        chart_path_d = temp_dir / "apartado_d.png"

        if isinstance(data_d, dict) and "totals" in data_d:
            data_d_plot = data_d["totals"]
        else:
            data_d_plot = data_d

        charts.create_donut_chart(
            labels=data_d_plot.index,
            values=data_d_plot.values,
            title="Gráfico D: Perfiles de EMO",
            out_path=chart_path_d,
        )
        writer.insert_content_at_anchor(
            doc,
            "Perfiles EMO",
            data_d_plot,
            chart_path_d,
            domain.generate_text_D(data_d),
        )

    # --- E) Vigencia EMO ---
    if "apartado_e" in stats:
        console.print("   - Procesando Apartado E ('Vigencia EMO')...")
        data_e = stats["apartado_e"]
        chart_path_e = temp_dir / "apartado_e.png"
        charts.create_barh_chart(
            labels=data_e.index,
            values=data_e.values,
            title="Gráfico E: Vigencia de EMO",
            out_path=chart_path_e,
        )
        writer.insert_content_at_anchor(
            doc,
            "Vigencia EMO",
            data_e,
            chart_path_e,
            domain.generate_text_E(data_e),
        )

    # --- F) Aptitud EMO (TRIPLE DONUT) ---
    if "apartado_f" in stats:
        console.print("   - Procesando Apartado F ('Aptitud EMO')...")
        data_f = stats["apartado_f"]
        chart_path_f = temp_dir / "apartado_f_triple.png"

        order = ["APTO", "CON RESTRICCIONES", "NO APTO", "OBSERVADO"]

        def normalize_aptitud_text(v: object) -> str:
            s = "" if pd.isna(v) else str(v).strip().upper()
            if "NO" in s and "APTO" in s:
                return "NO APTO"
            if "RESTR" in s:
                return "CON RESTRICCIONES"
            if "OBSERV" in s:
                return "OBSERVADO"
            if "APTO" in s:
                return "APTO"
            return "OBSERVADO"

        def normalize_sexo_text(v: object) -> str:
            s = "" if pd.isna(v) else str(v).strip().upper()
            if s in {"F", "FEMENINO", "MUJER"}:
                return "F"
            if s in {"M", "MASCULINO", "HOMBRE"}:
                return "M"
            return ""

        def normalize_counts_series(s: pd.Series) -> pd.Series:
            if s is None:
                return pd.Series([0, 0, 0, 0], index=order, dtype=int)
            ss = s.copy()
            ss.index = [str(i).strip().upper() for i in ss.index]
            alias_map = {
                "APTO CON RESTRICCIÓN": "CON RESTRICCIONES",
                "APTO CON RESTRICCION": "CON RESTRICCIONES",
                "CON RESTRICCION": "CON RESTRICCIONES",
                "CON RESTRICCIONES": "CON RESTRICCIONES",
            }
            ss = ss.rename(index=alias_map)
            ss = pd.to_numeric(ss, errors="coerce").fillna(0).astype(int)
            ss = ss.groupby(level=0).sum()
            ss = ss.reindex(order).fillna(0).astype(int)
            return ss

        if isinstance(data_f, dict):
            counts_total = normalize_counts_series(data_f.get("counts_total"))
            counts_f = normalize_counts_series(data_f.get("counts_f"))
            counts_m = normalize_counts_series(data_f.get("counts_m"))

        elif isinstance(data_f, pd.Series):
            # normalizar total desde la serie recibida
            counts_total = normalize_counts_series(data_f)

            # reconstruimos femenino/masculino desde df_activos
            if "sexo" not in df_activos.columns or "aptitud" not in df_activos.columns:
                console.print("[yellow]Advertencia F: faltan columnas 'sexo' o 'aptitud' en df_activos. Se usará 1 donut.[/yellow]")
                charts.create_donut_chart(
                    labels=counts_total.index,
                    values=counts_total.values,
                    title="Gráfico F: Aptitud de EMO",
                    out_path=chart_path_f,
                )
                writer.insert_content_at_anchor(
                    doc, "Aptitud EMO", counts_total, chart_path_f, domain.generate_text_F(data_f)
                )
                console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")
                return
            else:
                tmp = df_activos.copy()
                tmp["_sexo_norm"] = tmp["sexo"].apply(normalize_sexo_text)
                tmp["_apt_norm"] = tmp["aptitud"].apply(normalize_aptitud_text)

                counts_f = tmp[tmp["_sexo_norm"] == "F"]["_apt_norm"].value_counts().reindex(order).fillna(0).astype(int)
                counts_m = tmp[tmp["_sexo_norm"] == "M"]["_apt_norm"].value_counts().reindex(order).fillna(0).astype(int)
        else:
            console.print(f"[yellow]Advertencia F: formato no soportado en apartado_f -> {type(data_f)}[/yellow]")
            console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")
            return

        charts.create_triple_donut_aptitud(
            counts_f=counts_f,
            counts_total=counts_total,
            counts_m=counts_m,
            title="Gráfico N°04: EMOS SEGÚN APTITUD MÉDICA",
            out_path=chart_path_f,
        )

        writer.insert_content_at_anchor(
            doc,
            "Aptitud EMO",
            counts_total,  # tabla del total general
            chart_path_f,
            domain.generate_text_F(data_f),
        )

    console.print("[bold]Manejador del Reporte Estándar ha finalizado.[/bold]")