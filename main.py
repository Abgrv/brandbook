# Импортируем FastAPI — основной класс для создания веб-приложения
from fastapi import FastAPI

# Импортируем router из модуля users.routes — чтобы подключить роуты, связанные с пользователями
from backend.users.routes import router as users_router

# Создаём экземпляр приложения FastAPI
app = FastAPI(title="Brandbook API")  # Название API для документации

# Подключаем роутер users к основному приложению с префиксом /users (см. в users/routes.py)
app.include_router(users_router)

# Определяем корневой маршрут (GET /), который возвращает приветственное сообщение
@app.get("/")
def read_root():
    return {"message": "Welcome to Brandbook API"}

