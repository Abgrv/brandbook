# backend/auth/deps.py
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from config import JWT_SECRET, JWT_ALG
from backend.users import models as users_models

def current_user(request: Request, db: Session = Depends(get_db)) -> users_models.User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    user = db.query(users_models.User).get(user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
