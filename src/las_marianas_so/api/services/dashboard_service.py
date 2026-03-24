from las_marianas_so.api.services import standard_dashboard_service

def get_dashboard_data(report_type: str, data: dict, obra: str, year: int, month: int):
    report_type = (report_type or "").strip().lower()

    if report_type == "standard":
        return standard_dashboard_service.build_dashboard(data, obra, year, month)

    raise ValueError(f"report_type no soportado: {report_type}")