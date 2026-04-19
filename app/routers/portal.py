"""
商户和消费者 Web 门户路由
提供登录页面和仪表盘界面
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, hash_password
from app.models.user import User, UserRole
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/portal", tags=["portal"])

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def _read_template(name: str) -> str:
    with open(os.path.join(TEMPLATE_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


class PortalLoginRequest(BaseModel):
    email: str
    password: str


class PortalRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "consumer"


@router.get("/login", response_class=HTMLResponse)
def portal_login_page():
    """商户/消费者登录页面"""
    html = _read_template("login.html")
    return HTMLResponse(content=html)


@router.post("/do-login")
def portal_do_login(req: PortalLoginRequest, db: Session = Depends(get_db)):
    """处理登录请求，返回 token 和跳转地址"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if user.is_banned:
        raise HTTPException(status_code=403, detail=f"账号已被封禁：{user.ban_reason}")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号未激活")

    token = create_access_token({"sub": user.id})

    if user.role == UserRole.MERCHANT:
        redirect = f"/portal/merchant?token={token}"
    elif user.role == UserRole.ADMIN:
        redirect = "/admin"
    else:
        redirect = f"/portal/consumer?token={token}"

    return {"redirect": redirect, "token": token, "role": user.role.value}


@router.post("/do-register")
def portal_do_register(req: PortalRegisterRequest, db: Session = Depends(get_db)):
    """处理注册请求"""
    existing = db.query(User).filter(
        (User.email == req.email) | (User.username == req.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    role = UserRole.MERCHANT if req.role == "merchant" else UserRole.CONSUMER
    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        role=role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})

    if role == UserRole.MERCHANT:
        redirect = f"/portal/merchant?token={token}"
    else:
        redirect = f"/portal/consumer?token={token}"

    return {"redirect": redirect, "token": token, "role": role.value}


@router.get("/merchant", response_class=HTMLResponse)
def merchant_dashboard(token: str = ""):
    """商户仪表盘"""
    if not token:
        return RedirectResponse(url="/portal/login")
    html = _read_template("merchant_dashboard.html")
    html = html.replace("{{token}}", token)
    return HTMLResponse(content=html)


@router.get("/consumer", response_class=HTMLResponse)
def consumer_dashboard(token: str = ""):
    """消费者仪表盘"""
    if not token:
        return RedirectResponse(url="/portal/login")
    html = _read_template("consumer_dashboard.html")
    html = html.replace("{{token}}", token)
    return HTMLResponse(content=html)


@router.get("/logout")
def portal_logout():
    """退出登录"""
    return RedirectResponse(url="/portal/login")
