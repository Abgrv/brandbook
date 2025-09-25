# app/users/routes.py

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from database import get_db
from backend.users import models, schemas
from backend.auth.deps import current_user
from backend.users.models import User
from config import JWT_SECRET, JWT_ALG, JWT_EXPIRES_MIN

router = APIRouter(prefix="/users", tags=["Users"])

# 📌 Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📌 Настройки JWT
# SECRET_KEY = "supersecret"  # в реальном проекте — хранить в .env
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = JWT_SECRET
ALGORITHM = JWT_ALG
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_EXPIRES_MIN


# 🔹 Хэширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 🔹 Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 🔹 Генерация токена
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 📌 Регистрация пользователя
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, что email ещё не используется
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Создаём нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# 📌 Логин пользователя
@router.post("/login", response_model=schemas.Token)
def login(
    user: schemas.UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")


    # Генерация токена
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # кладём токен в HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False  # ⚠️ в проде лучше True (https)
    )
    return {"access_token": access_token, "token_type": "bearer"}


#Защищённый маршрут
@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": str(user.id), "email": user.email, "name": f"{user.first_name} {user.last_name}"}


# logout — очистка cookie
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


