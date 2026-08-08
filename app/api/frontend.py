from fastapi import APIRouter, Request, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth.dependencies import get_current_user
from app.models.user import User
from jose import JWTError
from typing import Optional

router = APIRouter(tags=["frontend"])
templates = Jinja2Templates(directory="frontend/templates")


# A soft dependency to check if a user is logged in via cookie/localStorage
# We primarily use localStorage for tokens, so pages will load unconditionally
# and client-side JS (app.js `requireAuth()`) will redirect if missing.
# However, Jinja might want to know if `current_user` exists.
# We'll just pass None and let JS handle auth redirects for simplicity,
# or we can write a mock for server-side rendering if needed.

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={})


@router.get("/import", response_class=HTMLResponse)
async def import_page(request: Request):
    return templates.TemplateResponse(request=request, name="import.html", context={})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html", context={})
