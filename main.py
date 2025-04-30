from fastapi import FastAPI, Form
import uuid
import os
import replicate
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI()  # <- ESTA LÍNEA DEBE ESTAR ANTES DE app.mount()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")
