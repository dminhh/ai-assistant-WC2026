# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, matches, competitions, standings, predictions, chat, admin
from app.scheduler.polling import start_scheduler, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="WC2026 Prediction API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(competitions.router)
app.include_router(standings.router)
app.include_router(predictions.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
