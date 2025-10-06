from fastapi import FastAPI
from . import models
from .database import engine
from app.routers import auth, accounts

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budgeting App Backend")

# Routers
app.include_router(auth.router)
app.include_router(accounts.router)

@app.get("/")
def root():
    return {"message": "Budgeting App API running"}