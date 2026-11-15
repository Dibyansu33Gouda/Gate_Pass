from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import require_role

router = APIRouter(tags=["Approvals"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/approvals", response_class=HTMLResponse)
def resident_approvals(request: Request, msg: str = None, error: str = None, user=Depends(require_role("resident"))):
    rid = user.get("resident_id")
    if not rid:
        return templates.TemplateResponse(request=request, name="approvals.html",
            context={"user": user, "error": "No resident linked.", "pending_visits": [], "recent_visits": [], "msg": None})

    with get_db_cursor() as (cur, _):
        cur.execute("""
            SELECT v.visit_id, vi.visitor_name, vi.phone AS visitor_phone, v.purpose, v.visit_date, s.staff_name AS guard_name
            FROM visits v JOIN visitors vi ON v.visitor_id = vi.visitor_id JOIN security_staff s ON v.staff_id = s.staff_id
            WHERE v.resident_id = %s AND v.approval_status = 'Pending' ORDER BY v.visit_id DESC
        """, (rid,))
        pending = cur.fetchall()

        cur.execute("""
            SELECT v.visit_id, vi.visitor_name, vi.phone AS visitor_phone, v.purpose, v.visit_date, v.approval_status, v.gate_pass_no, v.entry_time, v.exit_time
            FROM visits v JOIN visitors vi ON v.visitor_id = vi.visitor_id
            WHERE v.resident_id = %s AND v.approval_status != 'Pending' ORDER BY v.visit_id DESC LIMIT 10
        """, (rid,))
        recent = cur.fetchall()

        cur.execute("SELECT name, flat_no FROM residents WHERE resident_id = %s", (rid,))
        r_info = cur.fetchone()

    return templates.TemplateResponse(request=request, name="approvals.html",
        context={"user": user, "resident_info": r_info, "pending_visits": pending, "recent_visits": recent, "msg": msg, "error": error})

@router.post("/approvals/{visit_id}/approve")
def approve_visit(visit_id: int, user=Depends(require_role("resident"))):
    rid = user.get("resident_id")
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("""
            UPDATE visits SET approval_status = 'Approved',
                gate_pass_no = CONCAT('GP-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(visit_id, 4, '0'))
            WHERE visit_id = %s AND resident_id = %s AND approval_status = 'Pending'
        """, (visit_id, rid))
        if cur.rowcount == 0:
            return RedirectResponse("/approvals?error=Already+processed+or+unauthorized.", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/approvals?msg=Approved!+Gate+Pass+issued.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/approvals/{visit_id}/reject")
def reject_visit(visit_id: int, user=Depends(require_role("resident"))):
    rid = user.get("resident_id")
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE visits SET approval_status = 'Rejected' WHERE visit_id = %s AND resident_id = %s AND approval_status = 'Pending'", (visit_id, rid))
        if cur.rowcount == 0:
            return RedirectResponse("/approvals?error=Already+processed+or+unauthorized.", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/approvals?msg=Visit+rejected.", status_code=status.HTTP_303_SEE_OTHER)
