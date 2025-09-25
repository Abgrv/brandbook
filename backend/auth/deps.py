# backend/auth/deps.py
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from config import JWT_SECRET, JWT_ALG
from backend.users.models import User
from uuid import UUID

COOKIE_NAME = "access_token"

def _extract_token(request: Request) -> str | None:
    # 1) из cookie
    t = request.cookies.get(COOKIE_NAME)
    if t:
        return t
    # 2) из Authorization: Bearer ...
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None

def _parse_sub(sub: str):
    # пробуем int
    try:
        return int(sub)
    except Exception:
        pass
    # пробуем UUID
    try:
        return UUID(sub)
    except Exception:
        pass
    # оставляем строкой (если PK строковый)
    return sub

def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    key = _parse_sub(sub)

    # SQLAlchemy 1.4: Session.get; на 2.x используйте db.get(User, key)
    user = db.query(User).get(key)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
