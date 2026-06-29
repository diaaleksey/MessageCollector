from fastapi import FastAPI
import uvicorn
import time
from settings import DATABASE_URL
from db import Database
from routes import router

app = FastAPI(title="Remote Collector API")

@app.on_event("startup")
async def startup():
    # Инициализация БД и сохранение в состоянии приложения
    db = Database(DATABASE_URL)
    await db.init()
    app.state.db = db
    app.state.start_time = time.time()

@app.on_event("shutdown")
async def shutdown():
    # Закрытие соединения с БД, если оно существует
    if hasattr(app.state, 'db'):
        await app.state.db.close()

# Подключаем роутер с префиксом /api
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)