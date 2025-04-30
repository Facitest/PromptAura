from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
import os
import replicate
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

IMAGE_ENGINES = ["replicate"]
ENGINE_LIMITS = {
    "replicate": 100
}
ENGINE_USAGE = {
    "replicate": 0
}

BLACKLIST = ["nude", "weapon", "kill", "abuse", "racist"]

def is_prompt_clean(prompt: str) -> bool:
    lowered = prompt.lower()
    return not any(bad_word in lowered for bad_word in BLACKLIST)

def select_engine():
    for engine in IMAGE_ENGINES:
        if ENGINE_USAGE[engine] < ENGINE_LIMITS[engine]:
            return engine
    return "replicate"

def generate_image(prompt: str, engine: str) -> str:
    if engine == "replicate":
        try:
            ENGINE_USAGE[engine] += 1
            output = replicate_client.run(
                "stability-ai/sdxl:latest",
                input={"prompt": prompt}
            )
            return output[0] if isinstance(output, list) and output else ""
        except Exception as e:
            print("Replicate error:", e)
            return ""
    return ""

@app.post("/generate")
async def generate(prompt: str = Form(...), currency: str = Form(...), amount: str = Form(...)):
    if not is_prompt_clean(prompt):
        return {"error": "Prompt contains restricted content."}

    try:
        if float(amount) <= 0:
            return {"error": "Amount must be greater than 0."}
    except ValueError:
        return {"error": "Invalid amount."}

    engine = select_engine()
    image_url = generate_image(prompt, engine)

    if not image_url:
        return {"error": "Image generation failed. Try again later."}

    transaction_id = str(uuid.uuid4())

    return {
        "status": "success",
        "engine_used": engine,
        "image_url": image_url,
        "transaction_id": transaction_id,
        "paid_amount": amount,
        "currency": currency
    }
