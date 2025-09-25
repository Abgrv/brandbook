# backend/auth/deps.py
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from config import JWT_SECRET, JWT_ALG
from backend.users.models import User
from uuid import UUID

COOKIE_NAME = "access_token"

def _extract_token(request: Request):
    t = request.cookies.get(COOKIE_NAME)
    if t: return t
    a = request.headers.get("authorization") or request.headers.get("Authorization")
    if a and a.lower().startswith("bearer "): return a.split(" ",1)[1].strip()
    return None

def _parse_sub(sub: str):
    try: return int(sub)
    except: pass
    try: return UUID(sub)
    except: pass
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
    key = _parse_sub(str(sub))
    user = db.query(User).get(key)  # (на SA2.x: db.get(User, key))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
