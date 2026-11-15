from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from app.db import get_db_cursor
from app.auth import require_role
from app.schemas import StaffForm

router = APIRouter(tags=["Staff"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/staff", response_class=HTMLResponse)
def list_staff(request: Request, msg: str = None, error: str = None, user=Depends(require_role("admin"))):
    with get_db_cursor() as (cur, _):
        cur.execute("""
            SELECT s.staff_id, s.staff_name, s.phone, s.shift, s.is_active, COUNT(v.visit_id) AS visits_registered
            FROM security_staff s LEFT JOIN visits v ON s.staff_id = v.staff_id
            GROUP BY s.staff_id, s.staff_name, s.phone, s.shift, s.is_active ORDER BY s.staff_id
        """)
        staff_members = cur.fetchall()
    return templates.TemplateResponse(request=request, name="staff.html", context={"user": user, "staff_members": staff_members, "msg": msg, "error": error})

@router.post("/staff/new")
def add_staff(request: Request, staff_name: str = Form(...), phone: str = Form(...), shift: str = Form(...), user=Depends(require_role("admin"))):
    try:
        val = StaffForm(staff_name=staff_name, phone=phone, shift=shift)
    except ValueError as e:
        return RedirectResponse(f"/staff?error={e}", status_code=status.HTTP_303_SEE_OTHER)

    try:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("INSERT INTO security_staff (staff_name, phone, shift, is_active) VALUES (%s, %s, %s, TRUE)",
                        (val.staff_name, val.phone, val.shift))
    except mysql.connector.Error as err:
        msg = "Phone+already+exists." if err.errno == 1062 else f"DB+error:+{err.msg}"
        return RedirectResponse(f"/staff?error={msg}", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse("/staff?msg=Staff+member+added+successfully.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/staff/{staff_id}/update-shift")
def update_staff_shift(staff_id: int, shift: str = Form(...), user=Depends(require_role("admin"))):
    if shift in ["Morning", "Evening", "Night"]:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("UPDATE security_staff SET shift = %s WHERE staff_id = %s", (shift, staff_id))
        return RedirectResponse("/staff?msg=Shift+updated.", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/staff?error=Invalid+shift.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/staff/{staff_id}/toggle-active")
def toggle_staff_active(staff_id: int, user=Depends(require_role("admin"))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE security_staff SET is_active = NOT is_active WHERE staff_id = %s", (staff_id,))
    return RedirectResponse("/staff?msg=Staff+status+updated.", status_code=status.HTTP_303_SEE_OTHER)
