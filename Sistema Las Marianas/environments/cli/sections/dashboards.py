from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

NEON = "bright_green"


def run_dashboards(console: Console) -> None:
    console.print(Panel("Dashboards: próximamente.", border_style=NEON))