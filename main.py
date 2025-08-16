# Импортируем FastAPI — основной класс для создания веб-приложения
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Импортируем router из модуля users.routes — чтобы подключить роуты, связанные с пользователями
from backend.users.routes import router as users_router
from backend.brandbook.routes import router as brandbook_router

# Создаём экземпляр приложения FastAPI
app = FastAPI(title="Brandbook API")  # Название API для документации
app.mount('/frontend', StaticFiles(directory='frontend'), name='frontend')

# Подключаем роутер users к основному приложению с префиксом /users (см. в users/routes.py)
app.include_router(users_router)
app.include_router(brandbook_router)

@app.get('/', response_class=FileResponse)
async def read_home():
    return 'frontend/index.html'


