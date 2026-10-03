import os
import re
import json
import time
import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ValidationError
from google import genai

load_dotenv()

# Using GEMINI_API_KEY for consistency with the other two projects
# (this one used to be named GOOGLE_API_KEY).
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(
    title="AI Engineer API",
    description="AI-powered API with chat, email classification, and research report endpoints",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/app")
def serve_frontend():
    return FileResponse("frontend/index.html")


# --- Retry helper ---
# The AI provider's servers can be temporarily overloaded (503) or rate-limited
# (429). This retries a few times with increasing wait time before giving up.
def call_ai_with_retry(prompt_text, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model="gemini-3.6-flash", contents=prompt_text)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"AI call failed ({e}), retrying in {wait_time}s...")
            time.sleep(wait_time)


def describe_ai_error(e: Exception) -> str:
    """Turn a raw exception into a short, honest message instead of one
    generic 'something went wrong' for every kind of failure."""
    text = str(e)
    if "RESOURCE_EXHAUSTED" in text or "429" in text:
        return "Daily AI request limit reached for this API key. Try again later."
    if "UNAVAILABLE" in text or "503" in text:
        return "The AI service is temporarily overloaded. Please try again in a minute."
    return "The AI service returned an unexpected error."


def extract_json(raw_text: str) -> dict:
    """The AI sometimes wraps JSON in ```json ... ``` or adds a stray
    sentence before/after it. This pulls out just the {...} block so
    json.loads() has a real chance of succeeding."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in AI response: {raw_text[:200]}")
    return json.loads(match.group(0))


# --- Structured output schema for /classify ---
class EmailClassification(BaseModel):
    category: str
    urgency: str
    summary: str


class ChatRequest(BaseModel):
    message: str


class EmailRequest(BaseModel):
    email_text: str


class ResearchRequest(BaseModel):
    topic: str


@app.get("/")
def home():
    return {
        "message": "AI Engineer API is running",
        "endpoints": ["/chat", "/classify", "/research"],
        "built_by": "AI Engineer Portfolio Project"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = call_ai_with_retry(f"You are a helpful AI assistant. {request.message}")
    except Exception as e:
        return {"error": describe_ai_error(e)}
    return {
        "message": request.message,
        "reply": response.text
    }


@app.post("/classify")
def classify(request: EmailRequest):
    prompt = f"""You are an email classifier.
Read this email and return ONLY this JSON:
{{"category": "Support or Sales or Billing or Spam or Other",
  "urgency": "High or Medium or Low",
  "summary": "one sentence max 10 words"}}
Return only JSON. No extra text.
Email: {request.email_text}"""

    try:
        response = call_ai_with_retry(prompt)
        raw_json = extract_json(response.text)
        result = EmailClassification(**raw_json)
        return result.model_dump()
    except (ValueError, ValidationError) as e:
        print(f"[CLASSIFY FAILED] {type(e).__name__}: {e}")
        return {"error": "AI response didn't match the expected format. Please try again."}
    except Exception as e:
        print(f"[CLASSIFY FAILED] {type(e).__name__}: {e}")
        return {"error": describe_ai_error(e)}


@app.post("/research")
def research(request: ResearchRequest):
    prompt = f"""Write a structured research report about: {request.topic}
Include: summary, key facts, current trends, conclusion.
Keep it under 300 words."""

    try:
        response = call_ai_with_retry(prompt)
    except Exception as e:
        return {"error": describe_ai_error(e)}

    return {
        "topic": request.topic,
        "date": str(datetime.date.today()),
        "report": response.text
    }