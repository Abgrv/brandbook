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
from authlib.integrations.base_client.errors import OAuthError
from urllib.parse import urlencode

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
    client_kwargs={
        "scope": "openid email profile",
        "trust_env": False,
        "timeout": 10.0},
)

async def _authorize_google_token(request: Request, **kwargs) -> dict:
    """Обёртка вокруг authorize_access_token без дублирования redirect_uri."""
    app = oauth.google
    if request.scope.get("method", "GET") == "GET":
        error = request.query_params.get("error")
        if error:
            description = request.query_params.get("error_description")
            raise OAuthError(error=error, description=description)
        params = {
            "code": request.query_params.get("code"),
            "state": request.query_params.get("state"),
        }
    else:
        form = await request.form()
        params = {
            "code": form.get("code"),
            "state": form.get("state"),
        }

    session = None if app.framework.cache else request.session
    state = params.get("state")
    state_data = await app.framework.get_state_data(session, state)
    await app.framework.clear_state_data(session, state)
    params = app._format_state_params(state_data, params)

    claims_options = kwargs.pop("claims_options", None)
    claims_cls = kwargs.pop("claims_cls", None)
    leeway = kwargs.pop("leeway", 120)

    redirect_uri = params.pop("redirect_uri", None)
    token = await app.fetch_access_token(
        redirect_uri=redirect_uri,
        **params,
        **kwargs,
    )

    if "id_token" in token and state_data and "nonce" in state_data:
        userinfo = await app.parse_id_token(
            token,
            nonce=state_data["nonce"],
            claims_options=claims_options,
            claims_cls=claims_cls,
            leeway=leeway,
        )
        token["userinfo"] = userinfo
    return token


# def _resolve_redirect_uri(request: Request) -> str:
#     """Return redirect URI configured explicitly or build it from the current request."""

#     if not OAUTH_REDIRECT_URI or OAUTH_REDIRECT_URI.lower() == "auto":
#         # request.url_for уже вернёт абсолютный URL c текущим хостом/портом
#         return str(request.url_for("google_callback"))
#     return OAUTH_REDIRECT_URI

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
    # redirect_uri = _resolve_redirect_uri(request)
    # return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Принимаем ответ от Google, создаём/находим пользователя, ставим cookie с JWT."""
    # Authlib 1.3 начал пробрасывать redirect_uri в fetch_access_token из query params,
    # из-за чего при наличии redirect_uri в запросе получаем TypeError (дублирование kwargs).
    # Если фронтенд передал redirect_uri (куда отправить пользователя после логина),
    # сохраняем его и создаём новый Request без этого параметра для oauth.google.
    query_items = list(request.query_params.multi_items())
    final_redirect: Optional[str] = None
    filtered_items = []
    for key, value in query_items:
        if key == "redirect_uri" and value:
            final_redirect = value
            continue
        filtered_items.append((key, value))

    if len(filtered_items) != len(query_items):
        scope = dict(request.scope)
        scope["query_string"] = urlencode(filtered_items, doseq=True).encode()
        request = Request(scope, receive=request.receive)
    else:
        final_redirect = None
    try:
        token = await _authorize_google_token(request)
        userinfo: Optional[dict] = token.get("userinfo")
        if not userinfo:
            # иногда нужно явно распарсить id_token
            userinfo = await oauth.google.parse_id_token(request, token)
    except OAuthError as e:
        detail = e.description or e.error
        raise HTTPException(400, f"Google auth failed: {detail}")
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
    if final_redirect and not final_redirect.startswith("/"):
        final_redirect = None

    redirect_target = final_redirect or "/frontend/index.html"
    if final_redirect and not final_redirect.startswith("/"):
        final_redirect = None

    redirect_target = final_redirect or "/frontend/index.html"
    resp = RedirectResponse(url=redirect_target)
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
