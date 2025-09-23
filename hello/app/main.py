from fastapi import FastAPI
import os

app = FastAPI(title="Hello API", version="0.1.0")

@app.get("/")
def read_root():
    return {
        "message": "Hello from FastAPI on Kubernetes!",
        "version": app.version,
        "env": os.getenv("APP_ENV","dev"),
    }

@app.get("/healthz")
def health():
    return {
        "status": "ok"
    }

@app.get("/readyz")
def ready():
    return {
        "status": "ready"
    }
