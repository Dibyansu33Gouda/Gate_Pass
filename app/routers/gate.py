from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import require_role

router = APIRouter(tags=["Gate Operations"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/gate", response_class=HTMLResponse)
def gate_management(request: Request, msg: str = None, error: str = None, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor() as (cur, _):
        cur.execute("""
            SELECT v.visit_id, vi.visitor_name, vi.phone AS visitor_phone, r.name AS resident_name, r.flat_no, v.purpose, v.gate_pass_no, v.visit_date
            FROM visits v JOIN visitors vi ON v.visitor_id = vi.visitor_id JOIN residents r ON v.resident_id = r.resident_id
            WHERE v.approval_status = 'Approved' AND v.entry_time IS NULL ORDER BY v.visit_id DESC
        """)
        waiting = cur.fetchall()

        cur.execute("""
            SELECT v.visit_id, vi.visitor_name, vi.phone AS visitor_phone, r.name AS resident_name, r.flat_no, v.gate_pass_no, v.entry_time, v.purpose
            FROM visits v INNER JOIN visitors vi ON v.visitor_id = vi.visitor_id INNER JOIN residents r ON v.resident_id = r.resident_id
            WHERE v.entry_time IS NOT NULL AND v.exit_time IS NULL ORDER BY v.entry_time DESC
        """)
        inside = cur.fetchall()

    return templates.TemplateResponse(request=request, name="gate.html", context={"user": user, "waiting_for_entry": waiting, "visitors_inside": inside, "msg": msg, "error": error})

@router.post("/gate/{visit_id}/entry")
def record_entry(visit_id: int, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE visits SET entry_time = NOW() WHERE visit_id = %s AND approval_status = 'Approved' AND entry_time IS NULL", (visit_id,))
        if cur.rowcount == 0:
            return RedirectResponse("/gate?error=Entry+failed:+must+be+approved+and+not+entered.", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(f"/gate?msg=Entry+recorded+for+Visit+%23{visit_id}.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/gate/{visit_id}/exit")
def record_exit(visit_id: int, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE visits SET exit_time = NOW() WHERE visit_id = %s AND entry_time IS NOT NULL AND exit_time IS NULL", (visit_id,))
        if cur.rowcount == 0:
            return RedirectResponse("/gate?error=Exit+failed:+not+logged+inside.", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/gate?msg=Exit+recorded+successfully.", status_code=status.HTTP_303_SEE_OTHER)
