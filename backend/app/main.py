# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import auth
from app.scheduler.polling import start_scheduler, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="WC2026 Prediction API", version="1.0.0", lifespan=lifespan)
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}
