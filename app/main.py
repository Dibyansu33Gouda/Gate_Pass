from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from app import config
from app.auth import get_current_user
from app.routers import (
    auth, dashboard, visitors, residents, staff,
    approvals, gate, deliveries, history, reports
)

app = FastAPI(title="GatePass", description="Smart Visitor & Delivery Management", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, max_age=86400)
templates = Jinja2Templates(directory="app/templates")

for r in (auth, dashboard, visitors, residents, staff, approvals, gate, deliveries, history, reports):
    app.include_router(r.router)

@app.get("/")
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    target = {"admin": "/dashboard", "security": "/gate", "resident": "/approvals"}.get(user["role"], "/login")
    return RedirectResponse(target, status_code=status.HTTP_303_SEE_OTHER)

@app.exception_handler(403)
def forbidden_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request, name="error.html",
        context={"user": get_current_user(request), "status_code": 403, "title": "Access Denied",
                 "message": getattr(exc, "detail", "Permission denied.")},
        status_code=403
    )

@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request, name="error.html",
        context={"user": get_current_user(request), "status_code": 404, "title": "Page Not Found",
                 "message": "The requested page was not found."},
        status_code=404
    )
