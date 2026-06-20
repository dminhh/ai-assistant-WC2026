# app/main.py
from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="WC2026 Prediction API", version="1.0.0")
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}
