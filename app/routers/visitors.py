from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_raw_connection, get_db_cursor
from app.auth import require_role
from app.schemas import VisitorRegisterForm

router = APIRouter(tags=["Visitors"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/visitors/new", response_class=HTMLResponse)
def visitor_registration_form(request: Request, error: str = None, msg: str = None, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor() as (cur, _):
        cur.execute("SELECT resident_id, name, flat_no FROM residents WHERE is_active = TRUE ORDER BY flat_no, name")
        residents = cur.fetchall()
    return templates.TemplateResponse(request=request, name="visitors_new.html", context={"user": user, "residents": residents, "error": error, "msg": msg})

@router.post("/visitors/new")
def visitor_registration_submit(
    request: Request, visitor_name: str = Form(...), phone: str = Form(...),
    resident_id: int = Form(...), purpose: str = Form(...), user=Depends(require_role(["security", "admin"]))
):
    try:
        data = VisitorRegisterForm(visitor_name=visitor_name, phone=phone, resident_id=resident_id, purpose=purpose)
    except ValueError as e:
        return RedirectResponse(f"/visitors/new?error={e}", status_code=status.HTTP_303_SEE_OTHER)

    staff_id = user.get("staff_id") or 1
    conn = get_raw_connection()
    try:
        conn.start_transaction()
        cur = conn.cursor()
        cur.execute("SELECT visitor_id FROM visitors WHERE phone = %s", (data.phone,))
        row = cur.fetchone()
        if row:
            visitor_id = row[0]
            cur.execute("UPDATE visitors SET visitor_name = %s, is_active = TRUE WHERE visitor_id = %s", (data.visitor_name, visitor_id))
        else:
            cur.execute("INSERT INTO visitors (visitor_name, phone) VALUES (%s, %s)", (data.visitor_name, data.phone))
            visitor_id = cur.lastrowid

        cur.execute(
            "INSERT INTO visits (visitor_id, resident_id, staff_id, purpose, approval_status) VALUES (%s, %s, %s, %s, 'Pending')",
            (visitor_id, data.resident_id, staff_id, data.purpose)
        )
        visit_id = cur.lastrowid
        conn.commit()
        cur.close()
    except Exception as exc:
        conn.rollback()
        return RedirectResponse(f"/visitors/new?error=Transaction+failed:+{exc}", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        conn.close()

    return RedirectResponse(f"/visitors/new?msg=Visit+request+registered+successfully+(ID:+{visit_id}).", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/visitors", response_class=HTMLResponse)
def visitors_list(request: Request, q: str = None, msg: str = None, error: str = None, user=Depends(require_role(["security", "admin"]))):
    where = "WHERE v.visitor_name LIKE %s OR v.phone LIKE %s" if q else ""
    params = (f"%{q.strip()}%", f"%{q.strip()}%") if q else ()
    with get_db_cursor() as (cur, _):
        cur.execute(f"""
            SELECT v.visitor_id, v.visitor_name, v.phone, v.is_active,
                   COUNT(vi.visit_id) AS total_visits, MAX(vi.visit_date) AS last_visit_date
            FROM visitors v LEFT JOIN visits vi ON v.visitor_id = vi.visitor_id
            {where}
            GROUP BY v.visitor_id, v.visitor_name, v.phone, v.is_active
            ORDER BY v.visitor_id DESC
        """, params)
        visitors = cur.fetchall()
    return templates.TemplateResponse(request=request, name="visitors_list.html", context={"user": user, "visitors": visitors, "q": q or "", "msg": msg, "error": error})

@router.post("/visitors/{visitor_id}/toggle-active")
def toggle_visitor_active(visitor_id: int, user=Depends(require_role(["admin", "security"]))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE visitors SET is_active = NOT is_active WHERE visitor_id = %s", (visitor_id,))
    return RedirectResponse("/visitors?msg=Visitor+status+updated.", status_code=status.HTTP_303_SEE_OTHER)
