from typing import Optional
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
import os

ALGORITHM = os.getenv("JWT_ALG", "HS256")
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
COOKIE_NAME = "access_token"

class AuthError(HTTPException):
    def __init__(self, detail: str, code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=code, detail=detail)

def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get(COOKIE_NAME)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise AuthError("Invalid or expired token") from e

def get_current_user_payload(request: Request) -> dict:
    token = get_token_from_cookie(request)
    if not token:
        raise AuthError("Missing access token")
    return decode_token(token)
