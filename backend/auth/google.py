# backend/auth/google.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt
from sqlalchemy.orm import Session
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth

from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_REDIRECT_URI,
    JWT_SECRET, JWT_ALG, JWT_EXPIRES_MIN
)
from database import get_db
from backend.users import models as users_models

router = APIRouter(prefix="/auth/google", tags=["OAuth: Google"])

# --- Настройка OAuth-клиента ---
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile", "trust_env": False,
        "timeout": 10.0},
)

def issue_jwt(user_id) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRES_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

@router.get("/login")
async def google_login(request: Request):
    """Редирект на Google для логина/регистрации."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(500, "Google OAuth is not configured")
    return await oauth.google.authorize_redirect(request, OAUTH_REDIRECT_URI)

@router.get("/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Принимаем ответ от Google, создаём/находим пользователя, ставим cookie с JWT."""
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo: Optional[dict] = token.get("userinfo")
        if not userinfo:
            # иногда нужно явно распарсить id_token
            userinfo = await oauth.google.parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(400, f"Google auth failed: {e}")

    email = userinfo.get("email")
    sub = userinfo.get("sub")                     # устойчивый id в Google
    given_name = userinfo.get("given_name") or ""
    family_name = userinfo.get("family_name") or ""
    picture = userinfo.get("picture")

    if not email or not sub:
        raise HTTPException(400, "Missing email/sub from Google")

    # 1) ищем по provider+provider_id
    user = db.query(users_models.User).filter(
        users_models.User.provider == "google",
        users_models.User.provider_id == sub
    ).one_or_none()

    # 2) если нет — пробуем по email (мог регаться ранее паролем)
    if not user:
        user = db.query(users_models.User).filter(
            users_models.User.email == email
        ).one_or_none()

    # 3) создаём или обновляем
    if not user:
        user = users_models.User(
            first_name=given_name or "Google",
            last_name=family_name or "User",
            email=email,
            password_hash=None,     # OAuth-пользователь — пароль не обязателен
            provider="google",
            provider_id=sub,
            avatar_url=picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        changed = False
        if not user.provider:
            user.provider = "google"; changed = True
        if not user.provider_id:
            user.provider_id = sub; changed = True
        if picture and user.avatar_url != picture:
            user.avatar_url = picture; changed = True
        if changed:
            db.add(user)
            db.commit()

    # 4) выдаём JWT -> кладём в httpOnly cookie
    token_jwt = issue_jwt(user.id)
    resp = RedirectResponse(url="/frontend/index.html")
    resp.set_cookie(
        key="access_token",
        value=token_jwt,
        httponly=True,
        secure=False,   # True на проде (https)
        samesite="lax",
        max_age=JWT_EXPIRES_MIN * 60,
        path="/",
    )
    return resp
