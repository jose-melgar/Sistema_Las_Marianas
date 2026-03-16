from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

NEON = "bright_green"


def run_modelo_predictivo(console: Console) -> None:
    console.print(Panel("Modelo predictivo: próximamente.", border_style=NEON))