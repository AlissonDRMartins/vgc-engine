# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints

app = FastAPI()

app.include_router(endpoints.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # ou uma lista específica de domínios permitidos
    allow_credentials=True,
    allow_methods=[""],  # precisa permitir OPTIONS, POST, etc.
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, frontend!"}
