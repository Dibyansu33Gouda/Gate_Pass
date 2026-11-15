from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from app.db import get_db_cursor
from app.auth import require_role
from app.schemas import ResidentForm

router = APIRouter(tags=["Residents"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/residents", response_class=HTMLResponse)
def list_residents(request: Request, q: str = None, msg: str = None, error: str = None, user=Depends(require_role("admin"))):
    where = "WHERE r.name LIKE %s OR r.flat_no LIKE %s" if q else ""
    params = (f"%{q.strip()}%", f"%{q.strip()}%") if q else ()
    with get_db_cursor() as (cur, _):
        cur.execute(f"""
            SELECT r.resident_id, r.name, r.flat_no, r.phone, r.email, r.is_active, COUNT(v.visit_id) AS total_visits
            FROM residents r LEFT JOIN visits v ON r.resident_id = v.resident_id
            {where} GROUP BY r.resident_id, r.name, r.flat_no, r.phone, r.email, r.is_active
            ORDER BY r.flat_no, r.name
        """, params)
        residents = cur.fetchall()
    return templates.TemplateResponse(request=request, name="residents.html", context={"user": user, "residents": residents, "q": q or "", "msg": msg, "error": error})

@router.post("/residents/new")
def add_resident(request: Request, name: str = Form(...), flat_no: str = Form(...), phone: str = Form(...), email: str = Form(None), user=Depends(require_role("admin"))):
    try:
        val = ResidentForm(name=name, flat_no=flat_no, phone=phone, email=email.strip() if email and email.strip() else None)
    except ValueError as e:
        return RedirectResponse(f"/residents?error={e}", status_code=status.HTTP_303_SEE_OTHER)

    try:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("INSERT INTO residents (name, flat_no, phone, email, is_active) VALUES (%s, %s, %s, %s, TRUE)",
                        (val.name, val.flat_no, val.phone, val.email))
    except mysql.connector.Error as err:
        err_msg = "Duplicate+phone+or+email+already+exists." if err.errno == 1062 else f"DB+error:+{err.msg}"
        return RedirectResponse(f"/residents?error={err_msg}", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse("/residents?msg=Resident+added+successfully.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/residents/{resident_id}/toggle-active")
def toggle_resident_active(resident_id: int, user=Depends(require_role("admin"))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE residents SET is_active = NOT is_active WHERE resident_id = %s", (resident_id,))
    return RedirectResponse("/residents?msg=Resident+status+updated.", status_code=status.HTTP_303_SEE_OTHER)
