from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

# Контекст шифрования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Получить пользователя по email из базы
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Создать нового пользователя: хешируем пароль и сохраняем в БД
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)      # Добавляем в сессию
    db.commit()          # Сохраняем изменения
    db.refresh(db_user)  # Обновляем объект с учётом сохранённых данных (например, id)
    return db_user
