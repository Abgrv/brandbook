# app/users/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Annotated
from pydantic import StringConstraints
import uuid


# 📌 Схема для создания пользователя (при регистрации)
class UserCreate(BaseModel):
    # Имя — максимум 50 символов
    first_name: Annotated[str, StringConstraints(max_length=50)]
    # Фамилия — максимум 50 символов
    last_name: Annotated[str, StringConstraints(max_length=50)]
    # Email в правильном формате
    email: EmailStr
    # Пароль — минимум 8, максимум 128 символов
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


# 📌 Схема для отображения информации о пользователе (без пароля)
class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True  # Позволяет работать напрямую с SQLAlchemy объектами


# 📌 Параметры для авторизации пользователя
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 📌 Ответ при успешной авторизации
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
