# app/main.py
from fastapi import FastAPI

app = FastAPI(title="WC2026 Prediction API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}
