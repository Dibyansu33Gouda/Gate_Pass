from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import require_role

router = APIRouter(tags=["Reports"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/reports", response_class=HTMLResponse)
def admin_reports(request: Request, user=Depends(require_role("admin"))):
    with get_db_cursor() as (cur, _):
        # 1. Subquery with HAVING (Section 7, Query 6)
        cur.execute("""
            SELECT r.resident_id, r.name, r.flat_no, COUNT(*) AS total_visits
            FROM residents r JOIN visits v ON v.resident_id = r.resident_id
            GROUP BY r.resident_id, r.name, r.flat_no
            HAVING COUNT(*) > (SELECT AVG(cnt) FROM (SELECT COUNT(*) AS cnt FROM visits GROUP BY resident_id) AS per_resident)
            ORDER BY total_visits DESC
        """)
        above_avg = cur.fetchall()

        cur.execute("SELECT ROUND(AVG(cnt), 2) AS avg_v FROM (SELECT COUNT(*) AS cnt FROM visits GROUP BY resident_id) AS temp")
        row = cur.fetchone()
        society_avg = row["avg_v"] if row and row["avg_v"] else 0.0

        # 2. GROUP BY + COUNT (Query 4)
        cur.execute("""
            SELECT r.resident_id, r.name, r.flat_no, COUNT(v.visit_id) AS total_visits
            FROM residents r LEFT JOIN visits v ON r.resident_id = v.resident_id
            GROUP BY r.resident_id, r.name, r.flat_no ORDER BY total_visits DESC
        """)
        v_per_res = cur.fetchall()

        # 3. LEFT JOIN (Query 3)
        cur.execute("""
            SELECT r.resident_id, r.name AS resident_name, r.flat_no, d.delivery_id, d.delivery_type, d.status AS delivery_status, d.arrived_at
            FROM residents r LEFT JOIN deliveries d ON r.resident_id = d.resident_id ORDER BY r.resident_id, d.arrived_at DESC
        """)
        lj_deliv = cur.fetchall()

        # 4 & 5. Aggregates (Query 5)
        cur.execute("SELECT visit_date, COUNT(*) AS visitor_count FROM visits GROUP BY visit_date ORDER BY visit_date DESC LIMIT 14")
        daily = cur.fetchall()
        cur.execute("SELECT status, COUNT(*) AS count FROM deliveries GROUP BY status")
        d_status = cur.fetchall()

    return templates.TemplateResponse(request=request, name="reports.html",
        context={"user": user, "above_avg_residents": above_avg, "society_avg": society_avg, "visits_per_resident": v_per_res,
                 "left_join_deliveries": lj_deliv, "daily_counts": daily, "delivery_status_counts": d_status})
