from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

NEON = "bright_green"


def run_matriz_riesgos(console: Console) -> None:
    console.print(Panel("Matriz de riesgos: próximamente.", border_style=NEON))