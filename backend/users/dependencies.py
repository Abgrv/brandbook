# app/users/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from backend.users import models

# 📌 Настройки для JWT
SECRET_KEY = "supersecret"  # ⚠ хранить в .env
ALGORITHM = "HS256"

# 📌 Указываем FastAPI, что токен будет передаваться в формате Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# 🆕 NEW CODE — Получение текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Декодирует JWT-токен, извлекает ID пользователя,
    находит его в базе и возвращает объект пользователя.
    Если токен некорректен или пользователь не найден — ошибка 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось авторизовать пользователя",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ищем пользователя в БД
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user
