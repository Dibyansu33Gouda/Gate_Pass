from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import require_role

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, user=Depends(require_role("admin"))):
    with get_db_cursor() as (cur, _):
        cur.execute("SELECT COUNT(*) AS c FROM residents WHERE is_active = TRUE")
        res_cnt = cur.fetchone()["c"]
        cur.execute("SELECT SUM(visit_date = CURRENT_DATE) AS today, SUM(approval_status = 'Pending') AS pending, SUM(entry_time IS NOT NULL AND exit_time IS NULL) AS inside FROM visits")
        v_stats = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS total, COALESCE(SUM(status='Arrived'),0) AS arrived, COALESCE(SUM(status='Received'),0) AS received FROM deliveries")
        d_stats = cur.fetchone()

        cur.execute("""
            SELECT v.visit_id, vi.visitor_name, r.name AS resident_name, r.flat_no, v.purpose, v.approval_status, v.gate_pass_no
            FROM visits v JOIN visitors vi ON v.visitor_id = vi.visitor_id JOIN residents r ON v.resident_id = r.resident_id
            ORDER BY v.visit_id DESC LIMIT 5
        """)
        recent_visits = cur.fetchall()

        cur.execute("""
            SELECT d.delivery_id, r.name AS resident_name, r.flat_no, da.agent_name, da.courier_company, d.delivery_type, d.status, d.arrived_at
            FROM deliveries d JOIN residents r ON d.resident_id = r.resident_id JOIN delivery_agents da ON d.agent_id = da.agent_id
            ORDER BY d.delivery_id DESC LIMIT 5
        """)
        recent_deliveries = cur.fetchall()

    return templates.TemplateResponse(
        request=request, name="dashboard.html",
        context={
            "user": user,
            "stats": {
                "total_residents": res_cnt,
                "today_visitors": v_stats["today"] or 0,
                "pending_approvals": v_stats["pending"] or 0,
                "visitors_inside": v_stats["inside"] or 0,
                "arrived_deliveries": d_stats["arrived"] or 0,
                "received_deliveries": d_stats["received"] or 0,
                "total_deliveries": d_stats["total"] or 0
            },
            "recent_visits": recent_visits, "recent_deliveries": recent_deliveries
        }
    )
