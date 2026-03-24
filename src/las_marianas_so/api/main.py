from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from las_marianas_so.loader.core import ExcelLoader
from las_marianas_so.api.services.dashboard_service import get_dashboard_data
from pathlib import Path

app = FastAPI(title="Sistema Las Marianas API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_BASE_PATH = Path(__file__).resolve().parent.parent.parent.parent
_loader = ExcelLoader(_BASE_PATH)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/dashboard")
def dashboard(
    report_type: str = Query("standard"),
    obra: str = Query(...),
    year: int = Query(...),
    month: int = Query(...)
):
    data = _loader.get_data()
    return get_dashboard_data(report_type=report_type, data=data, obra=obra, year=year, month=month)

@app.get("/api/options/obras")
def obras():
    data = _loader.get_data()
    df = data.get("trabajadores")
    if df is None or "obra" not in df.columns:
        return {"items": []}
    items = sorted([str(x) for x in df["obra"].dropna().astype(str).unique()])
    return {"items": items}