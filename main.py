
from fastapi import FastAPI, Form
import uuid
import os
from dotenv import load_dotenv
import replicate

load_dotenv()
app = FastAPI()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

IMAGE_ENGINES = ["replicate", "huggingface", "backup"]
ENGINE_LIMITS = {
    "replicate": 100,
    "huggingface": 150,
    "backup": 9999
}
ENGINE_USAGE = {
    "replicate": 0,
    "huggingface": 0,
    "backup": 0
}

BLACKLIST = ["nude", "weapon", "kill", "abuse", "racist"]

def is_prompt_clean(prompt: str) -> bool:
    lowered = prompt.lower()
    return not any(bad_word in lowered for bad_word in BLACKLIST)

def select_engine():
    for engine in IMAGE_ENGINES:
        if ENGINE_USAGE[engine] < ENGINE_LIMITS[engine]:
            ENGINE_USAGE[engine] += 1
            return engine
    return "backup"

def generate_image(prompt: str, engine: str) -> str:
    if engine == "replicate":
        output = replicate_client.run(
            "stability-ai/stable-diffusion:db21e45c8a4b7d66f34663567ec61e2f21ff837f56d8f0030abf0c58628d4f48",
            input={"prompt": prompt}
        )
        return output[0] if output else ""
    else:
        image_id = uuid.uuid4()
        return f"https://cdn.promptaura.ai/generated/{engine}/{image_id}.png"

@app.post("/generate")
async def generate(prompt: str = Form(...), currency: str = Form(...), amount: str = Form(...)):
    if not is_prompt_clean(prompt):
        return {"error": "Prompt contains restricted content."}

    engine = select_engine()
    image_url = generate_image(prompt, engine)
    transaction_id = str(uuid.uuid4())

    return {
        "status": "success",
        "engine_used": engine,
        "image_url": image_url,
        "transaction_id": transaction_id,
        "paid_amount": amount,
        "currency": currency
    }
