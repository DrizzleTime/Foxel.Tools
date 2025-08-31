from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import onedrive, telegram

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onedrive.router, prefix="/api", tags=["onedrive"])
app.include_router(telegram.router, prefix="/api/tg", tags=["telegram"])

@app.get("/")
def read_root():
    return {"message": "Foxel.Tools API is running."}
