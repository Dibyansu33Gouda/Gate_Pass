from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_db_cursor
from app.auth import verify_password, get_current_user

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")
ROLE_HOME = {"admin": "/dashboard", "security": "/gate", "resident": "/approvals"}

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = None, msg: str = None):
    user = get_current_user(request)
    if user:
        return RedirectResponse(ROLE_HOME.get(user["role"], "/"), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error, "msg": msg, "user": None})

@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    u_clean = username.strip()
    with get_db_cursor() as (cur, _):
        cur.execute("SELECT user_id, username, password_hash, role, staff_id, resident_id FROM users WHERE username = %s", (u_clean,))
        user = cur.fetchone()
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            request=request, name="login.html", status_code=status.HTTP_400_BAD_REQUEST,
            context={"error": "Invalid username or password.", "user": None, "username_val": u_clean}
        )
    for k in ("user_id", "username", "role", "staff_id", "resident_id"):
        request.session[k] = user[k]
    return RedirectResponse(ROLE_HOME.get(user["role"], "/"), status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login?msg=You+have+been+logged+out+successfully.", status_code=status.HTTP_303_SEE_OTHER)
