# AI Engineer API

A production-ready REST API with 3 AI-powered endpoints built with FastAPI and Google Gemini.

## Endpoints
- GET / — API status and info
- POST /chat — AI conversation endpoint
- POST /classify — Email classifier returns JSON
- POST /research — AI research report generator

## Tools used
- Python
- FastAPI
- Google Gemini API (gemini-3.6-flash)
- Uvicorn

## How to run
1. Add your Google API key to .env file
2. Run: uvicorn main:app --reload
3. Open: http://127.0.0.1:8000/docs
4. Test all endpoints interactively

## Live Demo
All 3 endpoints tested and working with real AI responses.