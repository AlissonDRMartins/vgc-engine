# app/main.py
from fastapi import FastAPI
from app.api import endpoints

app = FastAPI()

app.include_router(endpoints.router)


@app.get("/")
def read_root():
    return {"message": "Hello, frontend!"}
