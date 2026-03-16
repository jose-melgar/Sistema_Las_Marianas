from __future__ import annotations

import argparse
from rich.console import Console

from environments.cli.splash_screen import SplashScreen
from environments.cli.audit_console import run as run_cli


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="las-marianas-so")
    parser.add_argument("--cli", action="store_true", help="Iniciar entorno CLI.")
    parser.add_argument("--no-splash", action="store_true", help="No mostrar splash.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()

    if args.cli:
        if not args.no_splash:
            try:
                s = SplashScreen()
                s.mostrar_banner()
                s.animacion_carga()
            except Exception:
                pass
        return run_cli()

    console.print("Ejecuta: python main.py --cli")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())