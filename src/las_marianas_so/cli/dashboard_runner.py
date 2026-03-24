from __future__ import annotations

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path


def _python_executable() -> str:
    return sys.executable


def run_dashboard(
    *,
    repo_root: Path,
    api_host: str = "127.0.0.1",
    api_port: int = 8000,
    web_port: int = 5500,
    open_browser: bool = True,
    reload: bool = False,
):
    """
    Levanta en paralelo:
      - API FastAPI (uvicorn) en http://{api_host}:{api_port}
      - Frontend estático (http.server) en http://{api_host}:{web_port}/static_dashboard/

    Nota:
      - reload=False recomendado al lanzarlo desde el menú (menos procesos zombie en Windows).
    """
    api_url = f"http://{api_host}:{api_port}"
    web_url = f"http://{api_host}:{web_port}/static_dashboard/"

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    api_cmd = [
        _python_executable(),
        "-m",
        "uvicorn",
        "las_marianas_so.api.main:app",
        "--host",
        api_host,
        "--port",
        str(api_port),
    ]
    if reload:
        api_cmd.append("--reload")

    web_cmd = [
        _python_executable(),
        "-m",
        "http.server",
        str(web_port),
        "--bind",
        api_host,
    ]

    api_proc = None
    web_proc = None

    try:
        print(f"[dashboard] Iniciando API en {api_url} ...")
        api_proc = subprocess.Popen(api_cmd, cwd=str(repo_root), env=env)

        time.sleep(1.2)

        print(f"[dashboard] Iniciando Frontend estático en {web_url} ...")
        web_proc = subprocess.Popen(web_cmd, cwd=str(repo_root), env=env)

        time.sleep(0.4)

        if open_browser:
            print(f"[dashboard] Abriendo navegador: {web_url}")
            webbrowser.open(web_url)

        print("[dashboard] Dashboard ejecutándose. Presiona Ctrl+C para detener.\n")

        while True:
            time.sleep(0.8)
            if api_proc.poll() is not None:
                raise RuntimeError("La API se detuvo inesperadamente.")
            if web_proc.poll() is not None:
                raise RuntimeError("El servidor web se detuvo inesperadamente.")

    except KeyboardInterrupt:
        print("\n[dashboard] Deteniendo procesos...")
    finally:
        for p in (web_proc, api_proc):
            if p is not None and p.poll() is None:
                p.terminate()
        print("[dashboard] Listo.")