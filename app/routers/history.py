from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import require_role

router = APIRouter(tags=["History"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/history", response_class=HTMLResponse)
def visit_history(request: Request, date: str = None, resident_name: str = None, approval_status: str = None, user=Depends(require_role(["security", "admin"]))):
    clauses, params = [], []
    if date and date.strip():
        clauses.append("visit_date = %s"); params.append(date.strip())
    if resident_name and resident_name.strip():
        clauses.append("resident_name LIKE %s"); params.append(f"%{resident_name.strip()}%")
    if approval_status in ["Pending", "Approved", "Rejected", "Cancelled"]:
        clauses.append("approval_status = %s"); params.append(approval_status)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_db_cursor() as (cur, _):
        cur.execute(f"SELECT * FROM v_visit_history {where} ORDER BY visit_date DESC, visit_id DESC LIMIT 100", tuple(params))
        history_records = cur.fetchall()
        cur.execute("SELECT DISTINCT name FROM residents WHERE is_active = TRUE ORDER BY name")
        resident_options = [r["name"] for r in cur.fetchall()]

    return templates.TemplateResponse(request=request, name="history.html",
        context={"user": user, "history_records": history_records, "resident_options": resident_options,
                 "selected_date": date or "", "selected_resident": resident_name or "", "selected_status": approval_status or "All"})
