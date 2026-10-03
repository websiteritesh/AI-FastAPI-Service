# AI Engineer API

A REST API with three AI-powered endpoints: conversational chat, structured email classification, and research report generation. Built with FastAPI and Google Gemini.

## Features

- **Three endpoints**: `/chat` for conversation, `/classify` for structured email classification, `/research` for report generation
- **Structured output** — `/classify` validates the AI's JSON response against a Pydantic schema instead of trusting raw text
- **Resilient AI calls** — automatic retries with exponential backoff if the AI provider is temporarily overloaded, with honest error messages distinguishing a quota limit from a real outage
- **A console-style web UI** — test all three endpoints from a browser, not just Swagger docs
- **Mocked tests** — the test suite fakes the AI response, so tests run in under a second and never touch your request quota
- **Dockerized** and **CI-tested** on every push

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| AI | Google Gemini API (`gemini-3.6-flash`) |
| Validation | Pydantic |
| Testing | pytest, httpx, unittest.mock |
| Deployment | Docker, Docker Compose |
| CI/CD | GitHub Actions |

## Project structure

```
project3_api/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_main.py
└── .github/workflows/
    └── ci.yml
```

## Endpoints

- `GET /` — API status and info
- `POST /chat` — `{"message": "..."}` → conversational reply
- `POST /classify` — `{"email_text": "..."}` → `{"category", "urgency", "summary"}`
- `POST /research` — `{"topic": "..."}` → `{"topic", "date", "report"}`

## Running locally

1. Create `.env` with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run:
   ```
   uvicorn main:app --reload
   ```
4. Open `http://127.0.0.1:8000/app` for the console UI, or `http://127.0.0.1:8000/docs` for interactive Swagger docs.

## Running with Docker

```
docker compose up --build
```

## Running tests

```
pytest -v
```

Tests use a mocked AI response, so they don't consume your Gemini API quota.
