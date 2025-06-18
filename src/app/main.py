# app/main.py

from fastapi import FastAPI
from src.app.routes.common_route import api_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(api_router)