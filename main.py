import os
import json
import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(
    title="AI Engineer API",
    description="AI-powered API built by an AI Engineer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"You are a helpful AI assistant. {request.message}"
    )
    return {
        "message": request.message,
        "reply": response.text
    }

@app.post("/classify")
def classify(request: EmailRequest):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""You are an email classifier.
Read this email and return ONLY this JSON:
{{"category": "Support or Sales or Billing or Spam or Other",
  "urgency": "High or Medium or Low",
  "summary": "one sentence max 10 words"}}
Return only JSON. No extra text.
Email: {request.email_text}"""
    )
    try:
        result = json.loads(response.text)
    except:
        result = {"raw": response.text}
    return result

@app.post("/research")
def research(request: ResearchRequest):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""Write a structured research report about: {request.topic}
Include: summary, key facts, current trends, conclusion.
Keep it under 300 words."""
    )
    return {
        "topic": request.topic,
        "date": str(datetime.date.today()),
        "report": response.text
    }