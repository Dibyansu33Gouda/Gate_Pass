from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
from app.db import get_db_cursor
from app.auth import require_role
from app.schemas import DeliveryForm, DeliveryAgentForm

router = APIRouter(tags=["Deliveries"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/deliveries", response_class=HTMLResponse)
def deliveries_page(request: Request, status_filter: str = None, msg: str = None, error: str = None, user=Depends(require_role(["security", "admin"]))):
    where = "WHERE d.status = %s" if status_filter in ["Arrived", "Received", "Returned"] else ""
    params = (status_filter,) if where else ()
    with get_db_cursor() as (cur, _):
        cur.execute(f"""
            SELECT d.delivery_id, r.name AS resident_name, r.flat_no, da.agent_name, da.phone AS agent_phone,
                   da.courier_company, s.staff_name AS guard_name, d.delivery_type, d.status, d.arrived_at, d.received_at
            FROM deliveries d JOIN residents r ON d.resident_id = r.resident_id
            JOIN delivery_agents da ON d.agent_id = da.agent_id JOIN security_staff s ON d.staff_id = s.staff_id
            {where} ORDER BY d.delivery_id DESC
        """, params)
        deliveries = cur.fetchall()
        cur.execute("SELECT resident_id, name, flat_no FROM residents WHERE is_active = TRUE ORDER BY flat_no, name")
        residents = cur.fetchall()
        cur.execute("SELECT agent_id, agent_name, phone, courier_company FROM delivery_agents ORDER BY courier_company, agent_name")
        agents = cur.fetchall()

    return templates.TemplateResponse(request=request, name="deliveries.html",
        context={"user": user, "deliveries": deliveries, "residents": residents, "agents": agents,
                 "status_filter": status_filter or "All", "msg": msg, "error": error})

@router.post("/deliveries/new")
def log_delivery(request: Request, resident_id: int = Form(...), agent_id: int = Form(...), delivery_type: str = Form(...), user=Depends(require_role(["security", "admin"]))):
    try:
        val = DeliveryForm(resident_id=resident_id, agent_id=agent_id, delivery_type=delivery_type)
    except ValueError as e:
        return RedirectResponse(f"/deliveries?error={e}", status_code=status.HTTP_303_SEE_OTHER)

    staff_id = user.get("staff_id") or 1
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("INSERT INTO deliveries (resident_id, staff_id, agent_id, delivery_type, status, arrived_at) VALUES (%s, %s, %s, %s, 'Arrived', NOW())",
                    (val.resident_id, staff_id, val.agent_id, val.delivery_type))
    return RedirectResponse("/deliveries?msg=Delivery+logged+successfully.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/deliveries/agent/new")
def register_delivery_agent(request: Request, agent_name: str = Form(...), phone: str = Form(...), courier_company: str = Form(...), user=Depends(require_role(["security", "admin"]))):
    try:
        val = DeliveryAgentForm(agent_name=agent_name, phone=phone, courier_company=courier_company)
    except ValueError as e:
        return RedirectResponse(f"/deliveries?error={e}", status_code=status.HTTP_303_SEE_OTHER)

    try:
        with get_db_cursor(commit=True) as (cur, _):
            cur.execute("INSERT INTO delivery_agents (agent_name, phone, courier_company) VALUES (%s, %s, %s)",
                        (val.agent_name, val.phone, val.courier_company))
    except mysql.connector.Error as err:
        msg = "Agent+phone+already+exists." if err.errno == 1062 else f"DB+error:+{err.msg}"
        return RedirectResponse(f"/deliveries?error={msg}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/deliveries?msg=Delivery+agent+registered.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/deliveries/{delivery_id}/receive")
def mark_delivery_received(delivery_id: int, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE deliveries SET status = 'Received', received_at = NOW() WHERE delivery_id = %s AND status = 'Arrived'", (delivery_id,))
    return RedirectResponse("/deliveries?msg=Delivery+marked+Received.", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/deliveries/{delivery_id}/return")
def mark_delivery_returned(delivery_id: int, user=Depends(require_role(["security", "admin"]))):
    with get_db_cursor(commit=True) as (cur, _):
        cur.execute("UPDATE deliveries SET status = 'Returned' WHERE delivery_id = %s AND status = 'Arrived'", (delivery_id,))
    return RedirectResponse("/deliveries?msg=Delivery+marked+Returned.", status_code=status.HTTP_303_SEE_OTHER)
